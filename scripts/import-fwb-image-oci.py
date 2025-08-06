import os
import sys
import argparse
import re
import zipfile
import tempfile
import oci
from oci.core import ComputeClient, BlockstorageClient
from oci.object_storage import ObjectStorageClient
from oci.core.models import (
    CreateImageDetails,
    ImageSourceViaObjectStorageTupleDetails
)
from oci.exceptions import ServiceError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify required environment variables are set
required_vars = [
    'OCI_REGION',
    'OCI_COMPARTMENT_ID',
    'OCI_BUCKET_NAME',
    'OCI_NAMESPACE'
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"[ERROR] Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these in the .env file or environment variables")
    sys.exit(1)

def upload_to_object_storage(file_path, bucket_name, object_name):
    """Upload file to OCI Object Storage"""
    try:
        config = oci.config.from_file()
        object_storage_client = ObjectStorageClient(config)
        
        namespace = os.environ['OCI_NAMESPACE']
        
        # Delete any existing object to avoid conflicts
        try:
            object_storage_client.delete_object(
                namespace_name=namespace,
                bucket_name=bucket_name,
                object_name=object_name
            )
            print(f"[INFO] Deleted existing object {object_name}")
        except ServiceError as e:
            if e.status == 404:
                print(f"[INFO] No existing object to delete: {object_name}")
            else:
                print(f"[WARNING] Error deleting existing object: {e}")
        
        # Upload the file
        with open(file_path, "rb") as f:
            object_storage_client.put_object(
                namespace_name=namespace,
                bucket_name=bucket_name,
                object_name=object_name,
                put_object_body=f
            )
            
        print(f"[INFO] Successfully uploaded {file_path} to oci://{namespace}@{bucket_name}/{object_name}")
        return True
    except ServiceError as e:
        print(f"[ERROR] Failed to upload file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error during upload: {e}")
        sys.exit(1)

def delete_existing_image(compute_client, image_name):
    """Delete image if one with same name exists"""
    try:
        # List images with the same display name
        images = compute_client.list_images(
            compartment_id=os.environ['OCI_COMPARTMENT_ID'],
            display_name=image_name
        ).data
        
        if images:
            image_id = images[0].id
            print(f"[INFO] Found existing image {image_id} with name {image_name}")
            compute_client.delete_image(image_id=image_id)
            print(f"[INFO] Deleted existing image {image_id}")
    except ServiceError as e:
        if e.status == 404:
            print(f"[INFO] No existing image found with name {image_name}")
        else:
            print(f"[WARNING] Error checking/deleting existing image: {e}")

def create_image_from_object(compute_client, object_name, image_name, description, version, build, license_type):
    """Create custom image from object storage"""
    try:
        # First delete any existing image with same name
        delete_existing_image(compute_client, image_name)
        
        # Create image from object storage
        create_image_details = CreateImageDetails(
            compartment_id=os.environ['OCI_COMPARTMENT_ID'],
            display_name=image_name,
            launch_mode="PARAVIRTUALIZED",
            image_source_details=ImageSourceViaObjectStorageTupleDetails(
                source_type="objectStorageTuple",
                namespace_name=os.environ['OCI_NAMESPACE'],
                bucket_name=os.environ['OCI_BUCKET_NAME'],
                object_name=object_name
            )
        )
        
        response = compute_client.create_image(create_image_details=create_image_details)
        image_id = response.data.id
        print(f"[INFO] Image creation started: {image_id}")
        
        # Wait for image to reach AVAILABLE state before updating tags
        print("[INFO] Waiting for image to reach AVAILABLE state...")
        while True:
            image = compute_client.get_image(image_id=image_id).data
            if image.lifecycle_state == "AVAILABLE":
                print("[INFO] Image is now AVAILABLE")
                break
            elif image.lifecycle_state == "FAILED":
                print("[ERROR] Image creation failed")
                sys.exit(1)
            elif image.lifecycle_state not in ["PROVISIONING", "IMPORTING", "AVAILABLE"]:
                print(f"[WARNING] Unexpected image state: {image.lifecycle_state}")
                break
            # Wait before checking again
            import time
            time.sleep(10)
        
        # Add tags to the image
        freeform_tags = {
            "owner": "fwbqa",
            "version": version,
            "build": build,
            "license_type": license_type,
            "description": description
        }
        
        compute_client.update_image(
            image_id=image_id,
            update_image_details=oci.core.models.UpdateImageDetails(
                freeform_tags=freeform_tags
            )
        )
        
        print(f"[SUCCESS] Created custom image {image_name} ({image_id}) from object {object_name}")
        return image_id
    except ServiceError as e:
        print(f"[ERROR] Failed to create image: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error during image creation: {e}")
        sys.exit(1)

def parse_filename(filename):
    """Parse zip filename to extract components for object name"""
    license_type = 'payg' if 'ONDEMAND' in filename.upper() else 'byol'
    
    version_match = re.search(r'-v(\d+)\.', filename)
    version = f'v{version_match.group(1)}' if version_match else 'v7'
    
    build_match = re.search(r'-build(\d+)-', filename)
    build = build_match.group(1) if build_match else '0000'
    
    return license_type, version, build

def extract_qcow2(zip_path):
    """Extract .qcow2 file from zip file to system temp directory"""
    temp_dir = os.path.join(tempfile.gettempdir(), 'fwb_import')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('.qcow2'):
                zip_ref.extract(file, temp_dir)
                return os.path.join(temp_dir, file)
    raise Exception(".qcow2 file not found in zip file")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload VM image to OCI Object Storage and create custom image.")
    parser.add_argument("zip_file", help="Path to FortiWeb image zip file")
    parser.add_argument("--bucket", default=os.environ.get('OCI_BUCKET_NAME'), help="Object Storage bucket name")
    parser.add_argument("--description", default="FortiWeb VM image", help="Image description")

    args = parser.parse_args()

    # Parse filename and construct object name
    license_type, version, build = parse_filename(args.zip_file)
    object_name = f"{license_type}/{version}/{build}.qcow2"
    image_name = f"fwb-{license_type}-{version}-{build}"
    
    # Extract and upload .qcow2 file
    print(f"\n[STEP 1] Extracting .qcow2 file from {args.zip_file}")
    qcow2_path = extract_qcow2(args.zip_file)
    print(f"    → Extracted to: {qcow2_path}")

    print(f"\n[STEP 2] Uploading to OCI Object Storage bucket {args.bucket}")
    print(f"    → Object Name: {object_name}")
    upload_to_object_storage(qcow2_path, args.bucket, object_name)
    
    # Create custom image
    print(f"\n[STEP 3] Creating custom image")
    print(f"    → Image Name: {image_name}")
    
    config = oci.config.from_file()
    compute_client = ComputeClient(config)
    
    image_id = create_image_from_object(
        compute_client,
        object_name,
        image_name,
        args.description,
        version,
        build,
        license_type
    )
    
    print(f"\n[FINAL] Created custom image ID for Terraform: {image_id}")
