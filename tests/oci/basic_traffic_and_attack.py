import time
import urllib3
import os
from dotenv import load_dotenv
from tests.common.test_utils import (
    get_server_pool_ip,
    get_instance_id,
    get_public_ip,
    process_template,
    configure_fortiweb,
    run_tests_for_instance,
    logger
)

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment variables
    USERNAME = os.environ["FORTIWEB_OCI_USERNAME"]
    PASSWORD = os.environ["FORTIWEB_OCI_PASSWORD"]
    CONFIG_TEMPLATE_PATH = "config/cloud-server-policy.conf.template"  # Path to template file
    
    try:
        # Get server pool IP from .env (will throw error if not defined)
        server_pool_ip = get_server_pool_ip("OCI_SERVER_POOL_IP")
        
        # Process template to generate config content in memory
        config_content = process_template(CONFIG_TEMPLATE_PATH, server_pool_ip)
        
        # Get instance IDs and public IPs from Terraform output
        byol_instance_id = get_instance_id("oci_byol_instance_hostname")
        byol_ip = get_public_ip("fwb_oci_byol_public_ip")
        
        # Note: Only testing BYOL as there is no PAYG for OCI
        
        # Configure BYOL instance if available
        if byol_ip:
            logger.info(f"Connecting to FortiWeb BYOL at {byol_ip}")
            configure_fortiweb(byol_ip, USERNAME, PASSWORD, config_content)
            
            # Wait for configuration to be applied before testing
            logger.info("Waiting for BYOL configuration to be applied...")
            time.sleep(5)  # Wait for 5 seconds
        else:
            logger.error("Cannot proceed without a valid BYOL public IP")
            exit(1)
            
        # Run tests on BYOL instance
        if not run_tests_for_instance("BYOL", byol_ip):
            exit(1)
            
    except Exception as e:
        logger.error(f"Configuration failed: {str(e)}")
        exit(1)
