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
    ensure_instance_running,
    run_tests_for_instance,
    logger
)

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Get credentials from environment variables
    USERNAME = os.environ["FORTIWEB_AWS_USERNAME"]
    PASSWORD = os.environ["FORTIWEB_AWS_PASSWORD"]
    CONFIG_TEMPLATE_PATH = "config/cloud-server-policy.conf.template"  # Path to template file
    
    try:
        # Get server pool IP from .env (will throw error if not defined)
        server_pool_ip = get_server_pool_ip("AWS_SERVER_POOL_IP")
        
        # Process template to generate config content in memory
        config_content = process_template(CONFIG_TEMPLATE_PATH, server_pool_ip)
        
        # Get instance IDs from Terraform output
        byol_instance_id = get_instance_id("aws_byol_instance_hostname")
        payg_instance_id = get_instance_id("aws_payg_instance_hostname")
        
        # Ensure BYOL instance is running
        if byol_instance_id:
            if not ensure_instance_running("BYOL", byol_instance_id):
                logger.error("Cannot proceed with BYOL instance")
                exit(1)
        else:
            logger.error("Cannot proceed without a valid BYOL instance ID")
            exit(1)
        
        # Ensure PAYG instance is running
        if payg_instance_id:
            if not ensure_instance_running("PAYG", payg_instance_id):
                logger.warning("Cannot proceed with PAYG instance, but continuing with BYOL")
        else:
            logger.warning("PAYG instance ID not available, skipping PAYG instance check")
        
        # Get public IPs from Terraform output        
        byol_ip = get_public_ip("fwb_aws_byol_public_ip")
        payg_ip = get_public_ip("fwb_aws_payg_public_ip")

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
            
        # Configure PAYG instance if available
        if payg_ip and payg_instance_id:
            logger.info(f"Connecting to FortiWeb PAYG at {payg_ip}")
            configure_fortiweb(payg_ip, USERNAME, PASSWORD, config_content)
            
            # Wait for configuration to be applied before testing
            logger.info("Waiting for PAYG configuration to be applied...")
            time.sleep(5)  # Wait for 5 seconds
        else:
            logger.warning("PAYG public IP or instance ID not available, skipping PAYG configuration")
            
        # Run tests on BYOL instance
        if not run_tests_for_instance("BYOL", byol_ip):
            exit(1)
            
        # Run tests on PAYG instance if available
        if payg_ip and payg_instance_id:
            if not run_tests_for_instance("PAYG", payg_ip):
                exit(1)
        else:
            logger.warning("PAYG public IP or instance ID not available, skipping PAYG tests")
            
    except Exception as e:
        logger.error(f"Configuration failed: {str(e)}")
        exit(1)
