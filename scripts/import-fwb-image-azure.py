import os
import sys
import argparse
import re
import zipfile
import tempfile
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.mgmt.compute import ComputeManagementClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import AzureError

# Load environment variables from .env file
load_dotenv()

# Verify required environment variables are set
required_vars = [
    'AZURE_STORAGE_ACCOUNT',
    'AZURE_RESOURCE_GROUP', 
    'AZURE_LOCATION',
    'AZURE_SUBSCRIPTION_ID'
]

missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"[ERROR] Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these in the .env file or environment variables")
    sys.exit(1)

MY_STORAGE_CONTAINER = 'fwb-vhd'

def upload_to_blob_storage(file_path, container_name, blob_name):
    """Upload file to Azure Blob Storage as page blob"""
    try:
        credential = DefaultAzureCredential()
        blob_service_client = BlobServiceClient(
            account_url=f"https://{os.environ['AZURE_STORAGE_ACCOUNT']}.blob.core.windows.net",
            credential=credential
        )
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Delete any existing blob to avoid conflicts with blob type
        try:
            blob_client.delete_blob()
            print(f"[INFO] Deleted existing blob {blob_name}")
        except AzureError as e:
            if "The specified blob does not exist" not in str(e):
                print(f"[INFO] No existing blob to delete: {blob_name}")
        
        # For VHD files, we need to ensure proper page blob alignment
        file_size = os.path.getsize(file_path)
        print(f"[INFO] VHD file size: {file_size} bytes")
        
        # Page blobs must be aligned to 512-byte boundaries
        # If the file isn't properly aligned, we need to handle it differently
        if file_size % 512 != 0:
            print(f"[WARNING] File size {file_size} is not aligned to 512-byte boundary")
            # For misaligned files, we'll create a page blob and upload pages manually
            aligned_size = ((file_size + 511) // 512) * 512
            print(f"[INFO] Creating page blob with aligned size: {aligned_size} bytes")
            blob_client.create_page_blob(aligned_size)
            
            # Upload in chunks
            chunk_size = 4 * 1024 * 1024  # 4MB chunks
            with open(file_path, "rb") as data:
                offset = 0
                while offset < file_size:
                    chunk = data.read(chunk_size)
                    if not chunk:
                        break
                    
                    # Calculate the end offset for this chunk
                    end_offset = min(offset + len(chunk) - 1, aligned_size - 1)
                    
                    # Upload this page range
                    blob_client.upload_pages(chunk, offset, end_offset)
                    offset += len(chunk)
        else:
            # File is properly aligned, use direct upload
            with open(file_path, "rb") as data:
                blob_client.upload_blob(
                    data, 
                    blob_type="PageBlob"
                )
        print(f"[INFO] Successfully uploaded {file_path} to blob {blob_name} as page blob")
        return True
    except AzureError as e:
        print(f"[ERROR] Failed to upload file: {e}")
        sys.exit(1)

def delete_existing_image(compute_client, image_name):
    """Delete image if one with same name exists"""
    try:
        compute_client.images.get(
            resource_group_name=os.environ['AZURE_RESOURCE_GROUP'],
            image_name=image_name
        )
        print(f"[INFO] Found existing image {image_name}")
        compute_client.images.begin_delete(
            resource_group_name=os.environ['AZURE_RESOURCE_GROUP'],
            image_name=image_name
        ).result()
        print(f"[INFO] Deleted existing image {image_name}")
    except AzureError as e:
        if "was not found" in str(e):
            print(f"[INFO] No existing image found with name {image_name}")
        else:
            print(f"[WARNING] Error checking/deleting existing image: {e}")

def create_image_from_blob(compute_client, blob_url, image_name, description, version, build, license_type):
    """Create managed image from blob storage"""
    try:
        # First delete any existing image with same name
        delete_existing_image(compute_client, image_name)
        
        # Create image definition
        image_def = {
            "location": os.environ['AZURE_LOCATION'],
            "storage_profile": {
                "os_disk": {
                    "os_type": "Linux",
                    "os_state": "Generalized",
                    "blob_uri": blob_url,
                    "storage_account_type": "Standard_LRS",  # Standard HDD LRS
                    "caching": "None"
                }
            },
            "hyper_v_generation": "V1"
        }
        
        compute_client.images.begin_create_or_update(
            resource_group_name=os.environ['AZURE_RESOURCE_GROUP'],
            image_name=image_name,
            parameters=image_def
        ).result()
        
        print(f"[SUCCESS] Created managed image {image_name}")
        return image_name
    except AzureError as e:
        print(f"[ERROR] Failed to create image: {e}")
        sys.exit(1)

def parse_filename(filename):
    """Parse zip filename to extract components for blob name"""
    license_type = 'payg' if 'ONDEMAND' in filename.upper() else 'byol'
    
    version_match = re.search(r'-v(\d+)\.', filename)
    version = f'v{version_match.group(1)}' if version_match else 'v7'
    
    build_match = re.search(r'-build(\d+)-', filename)
    build = build_match.group(1) if build_match else '0000'
    
    return license_type, version, build

def extract_vhd(zip_path):
    """Extract boot.vhd from zip file to system temp directory"""
    temp_dir = os.path.join(tempfile.gettempdir(), 'fwb_import')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('boot.vhd'):
                zip_ref.extract(file, temp_dir)
                return os.path.join(temp_dir, file)
    raise Exception("boot.vhd not found in zip file")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload VM image and create Azure managed image.")
    parser.add_argument("zip_file", help="Path to FortiWeb image zip file")
    parser.add_argument("--container", default=MY_STORAGE_CONTAINER, help="Storage container name")
    parser.add_argument("--description", default="FortiWeb VM image", help="Image description")

    args = parser.parse_args()

    # Parse filename and construct blob name
    license_type, version, build = parse_filename(args.zip_file)
    blob_name = f"{license_type}/{version}/{build}.vhd"
    image_name = f"fwb-{license_type}-{version}-{build}"
    
    # Extract and upload boot.vhd
    print(f"\n[STEP 1] Extracting boot.vhd from {args.zip_file}")
    vhd_path = extract_vhd(args.zip_file)
    print(f"    → Extracted to: {vhd_path}")

    print(f"\n[STEP 2] Uploading to Azure Blob Storage container {args.container}")
    print(f"    → Blob Name: {blob_name}")
    upload_to_blob_storage(vhd_path, args.container, blob_name)
    
    # Create managed image
    blob_url = f"https://{os.environ['AZURE_STORAGE_ACCOUNT']}.blob.core.windows.net/{args.container}/{blob_name}"
    print(f"\n[STEP 3] Creating managed image")
    print(f"    → Image Name: {image_name}")
    
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(
        credential,
        os.environ['AZURE_SUBSCRIPTION_ID']
    )
    
    image_name_result = create_image_from_blob(
        compute_client,
        blob_url,
        image_name,
        args.description,
        version,
        build,
        license_type
    )
    
    print(f"\n[FINAL] Created managed image: {image_name_result}")
