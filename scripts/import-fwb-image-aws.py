import boto3
import os
import time
import sys
import argparse
import re
import zipfile
import tempfile
from botocore.exceptions import ClientError

MY_SNAP_BUCKET = 'fwb-lzeyu'

def upload_to_s3(file_path, bucket, key):
    """Upload file to S3 bucket"""
    s3 = boto3.client('s3')
    try:
        s3.upload_file(file_path, bucket, key)
        print(f"[INFO] Successfully uploaded {file_path} to s3://{bucket}/{key}")
        return True
    except ClientError as e:
        print(f"[ERROR] Failed to upload file: {e}")
        sys.exit(1)

def delete_existing_snapshot(name):
    """Delete snapshot if one with same name exists"""
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_snapshots(Filters=[{'Name': 'tag:Name', 'Values': [name]}])
        if len(response['Snapshots']) > 0:
            snap_id = response['Snapshots'][0]['SnapshotId']
            print(f"[INFO] Found existing snapshot {snap_id} with name {name}")
            ec2.delete_snapshot(SnapshotId=snap_id)
            print(f"[INFO] Deleted existing snapshot {snap_id}")
    except ClientError as e:
        print(f"[WARNING] Error checking/deleting existing snapshot: {e}")

def import_snapshot(name, description, bucket, key, disk_format='VMDK'):
    ec2 = boto3.client('ec2')
    
    # First delete any existing snapshot with same name
    delete_existing_snapshot(name)
    
    try:
        response = ec2.import_snapshot(
            Description=description,
            DiskContainer={
                'Format': disk_format,
                'UserBucket': {
                    'S3Bucket': bucket,
                    'S3Key': key
                }
            }
        )
        task_id = response['ImportTaskId']
        
        # Tag the snapshot with its name
        ec2.create_tags(
            Resources=[task_id],
            Tags=[{'Key': 'Name', 'Value': name}]
        )
        print(f"[INFO] Started import snapshot task: {task_id}")
        return task_id
    except ClientError as e:
        print(f"[ERROR] Failed to start snapshot import: {e}")
        sys.exit(1)

def wait_for_completion(task_id, poll_interval=30):
    ec2 = boto3.client('ec2')
    print(f"[INFO] Waiting for import task '{task_id}' to complete...")
    while True:
        try:
            response = ec2.describe_import_snapshot_tasks(ImportTaskIds=[task_id])
            task = response['ImportSnapshotTasks'][0]
            status = task['SnapshotTaskDetail']['Status']
            progress = task['SnapshotTaskDetail'].get('Progress', '0')

            print(f"    → Status: {status} | Progress: {progress}%")

            if status.lower() == 'completed':
                snapshot_id = task['SnapshotTaskDetail']['SnapshotId']
                print(f"[SUCCESS] Snapshot imported: {snapshot_id}")
                return snapshot_id
            elif status.lower() in ['cancelled', 'deleted', 'failed']:
                print(f"[ERROR] Snapshot import failed with status: {status}")
                sys.exit(1)

            time.sleep(poll_interval)

        except ClientError as e:
            print(f"[ERROR] Failed to get task status: {e}")
            sys.exit(1)

def delete_existing_ami(name):
    """Delete AMI if one with same name exists"""
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_images(Filters=[{'Name': 'name', 'Values': [name]}])
        if len(response['Images']) > 0:
            ami_id = response['Images'][0]['ImageId']
            print(f"[INFO] Found existing AMI {ami_id} with name {name}")
            ec2.deregister_image(ImageId=ami_id)
            print(f"[INFO] Deleted existing AMI {ami_id}")
    except ClientError as e:
        print(f"[WARNING] Error checking/deleting existing AMI: {e}")

def create_ami_from_snapshot(snapshot_id, name, description, version, build, license_type):
    """Create AMI from snapshot and tag it"""
    ec2 = boto3.client('ec2')
    
    # First delete any existing AMI with same name
    delete_existing_ami(name)
    
    try:
        response = ec2.register_image(
            Name=name,
            Description=description,
            RootDeviceName='/dev/sda1',
            BlockDeviceMappings=[{
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'SnapshotId': snapshot_id,
                    'VolumeType': 'gp3'
                }
            }],
            VirtualizationType='hvm',
            Architecture='x86_64',
            EnaSupport=True
        )
        ami_id = response['ImageId']
        
        # Tag the AMI with Owner, version, build and license_type
        ec2.create_tags(
            Resources=[ami_id],
            Tags=[
                {'Key': 'owner', 'Value': 'fwbqa'},
                {'Key': 'version', 'Value': version},
                {'Key': 'build', 'Value': build},
                {'Key': 'license_type', 'Value': license_type},
            ]
        )
        print(f"[SUCCESS] Created AMI {ami_id} from snapshot {snapshot_id}")
        return ami_id
    except ClientError as e:
        print(f"[ERROR] Failed to create AMI: {e}")
        sys.exit(1)

def parse_filename(filename):
    """Parse zip filename to extract components for S3 key"""
    # Determine license type
    license_type = 'payg' if 'ONDEMAND' in filename.upper() else 'byol'
    
    # Extract version
    version_match = re.search(r'-v(\d+)(?:\.|-)', filename)
    version = f'v{version_match.group(1)}' if version_match else 'v7'
    
    # Extract build number
    build_match = re.search(r'-build(\d+)-', filename)
    build = build_match.group(1) if build_match else '0000'
    
    return license_type, version, build

def extract_vmdk(zip_path):
    """Extract boot.vmdk from zip file to system temp directory"""
    temp_dir = os.path.join(tempfile.gettempdir(), 'fwb_import')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('boot.vmdk'):
                zip_ref.extract(file, temp_dir)
                return os.path.join(temp_dir, file)
    raise Exception("boot.vmdk not found in zip file")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload VM image, import snapshot, and create AMI.")
    parser.add_argument("zip_file", help="Path to FortiWeb image zip file")
    parser.add_argument("--bucket", default=MY_SNAP_BUCKET, help="S3 bucket name")
    parser.add_argument("--description", default="FortiWeb VM snapshot", help="Snapshot description")

    args = parser.parse_args()

    # Parse filename and construct S3 key
    license_type, version, build = parse_filename(args.zip_file)
    s3_key = f"vmdk/{license_type}/{version}/{build}.vmdk"
    ami_name = f"fwb-{license_type}-{version}-{build}"
    
    # Extract and upload boot.vmdk
    print(f"\n[STEP 1] Extracting boot.vmdk from {args.zip_file}")
    vmdk_path = extract_vmdk(args.zip_file)
    print(f"    → Extracted to: {vmdk_path}")

    print(f"\n[STEP 2] Uploading to S3 bucket {args.bucket}")
    print(f"    → S3 Key: {s3_key}")
    upload_to_s3(vmdk_path, args.bucket, s3_key)
    print(f"    → Upload complete: s3://{args.bucket}/{s3_key}")

    # Import snapshot with name
    snapshot_name = f"fwb-{license_type}-{version}-{build}"
    print(f"\n[STEP 3] Importing snapshot from S3")
    print(f"    → Snapshot Name: {snapshot_name}")
    task_id = import_snapshot(snapshot_name, args.description, args.bucket, s3_key)
    snapshot_id = wait_for_completion(task_id)

    # Create AMI from snapshot
    print(f"\n[STEP 4] Creating AMI from snapshot")
    print(f"    → AMI Name: {ami_name}")
    ami_id = create_ami_from_snapshot(snapshot_id, ami_name, args.description, version, build, license_type)
    print(f"\n[FINAL] AMI ID for Terraform: {ami_id}")
