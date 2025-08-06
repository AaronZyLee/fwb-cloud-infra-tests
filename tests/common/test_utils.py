import paramiko
import subprocess
import logging
import os
import requests
import json
import time
import urllib3
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_server_pool_ip(env_var_name):
    """Get server pool IP from .env file - throws error if not defined"""
    load_dotenv()
    server_pool_ip = os.getenv(env_var_name)
    if not server_pool_ip:
        logger.error(f"{env_var_name} not found in .env file")
        raise ValueError(f"{env_var_name} not found in .env file")
    logger.info(f"Server pool IP loaded from .env: {env_var_name}")
    return server_pool_ip

def get_instance_id(output_name):
    """Get instance ID from terraform output"""
    try:
        result = subprocess.run(
            ["terraform", "output", "-raw", output_name],
            capture_output=True,
            text=True,
            check=True
        )
        instance_id = result.stdout.strip()
        if not instance_id or "No outputs found" in instance_id:
            logger.error(f"No instance ID output found in Terraform for {output_name}")
            return None
        logger.info(f"Found instance ID for {output_name}: {instance_id}")
        return instance_id
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get instance ID: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Error getting instance ID: {str(e)}")
        return None

def get_instance_state(instance_id):
    """Get the state of an AWS instance using AWS CLI"""
    try:
        result = subprocess.run(
            ["aws", "ec2", "describe-instances", "--instance-ids", instance_id, "--query", "Reservations[0].Instances[0].State.Name", "--output", "text"],
            capture_output=True,
            text=True,
            check=True
        )
        state = result.stdout.strip()
        logger.info(f"Instance {instance_id} state: {state}")
        return state
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get instance state: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Error getting instance state: {str(e)}")
        return None

def start_instance(instance_id):
    """Start an AWS instance using AWS CLI"""
    try:
        logger.info(f"Starting instance {instance_id}...")
        result = subprocess.run(
            ["aws", "ec2", "start-instances", "--instance-ids", instance_id],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Started instance {instance_id}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start instance: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error starting instance: {str(e)}")
        return False

def refresh_terraform_state():
    """Refresh Terraform state"""
    try:
        logger.info("Refreshing Terraform state...")
        result = subprocess.run(
            ["terraform", "refresh"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("Terraform state refreshed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to refresh Terraform state: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error refreshing Terraform state: {str(e)}")
        return False

def get_public_ip(output_name):
    """Get FortiWeb public IP from terraform output"""
    try:
        result = subprocess.run(
            ["terraform", "output", "-raw", output_name],
            capture_output=True,
            text=True,
            check=True
        )
        ip = result.stdout.strip()
        if not ip or "No outputs found" in ip:
            logger.error(f"No public IP output found in Terraform for {output_name}")
            return None
        return ip
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get public IP: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Error getting public IP: {str(e)}")
        return None

def process_template(template_path, server_pool_ip):
    """Process template file and return the content as string"""
    try:
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Replace variables in template
        processed_content = template_content.replace('{{server_pool_ip}}', server_pool_ip)
        
        logger.info("Processed template in memory")
        return processed_content
    except Exception as e:
        logger.error(f"Failed to process template: {str(e)}")
        raise

def configure_fortiweb(ip, username, password, config_content):
    """SSH to FortiWeb and apply configuration"""
    try:
        # Connect to FortiWeb
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password)

        # Execute config directly from memory
        stdin, stdout, stderr = client.exec_command(config_content)

        # Log output
        logger.info(stdout.read().decode())
        if stderr.read():
            logger.error(stderr.read().decode())

    except Exception as e:
        logger.error(f"SSH connection failed: {str(e)}")
        raise
    finally:
        client.close()

def test_http_healthcheck(ip):
    """Test HTTPS connectivity to FortiWeb (with self-signed cert handling)"""
    try:
        response = requests.get(f"https://{ip}/", 
                              timeout=5,
                              verify=False)
        if response.status_code == 200:
            logger.info("HTTPS health check passed (200 OK)")
            return True
        else:
            logger.error(f"HTTPS health check failed: Status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"HTTPS health check error: {str(e)}")
        return False

def test_blocked_user_agent(ip):
    """Test that requests with User-Agent: ApacheBench are blocked"""
    try:
        headers = {'User-Agent': 'ApacheBench'}
        response = requests.get(f"https://{ip}/", 
                              headers=headers,
                              timeout=5,
                              verify=False)
        
        # Check if request is blocked (should not be 200 OK)
        if response.status_code != 200:
            logger.info(f"Blocked User-Agent test passed: Status {response.status_code} (expected non-200)")
            return True
        else:
            logger.error("Blocked User-Agent test failed: Request was not blocked (200 OK)")
            return False
    except Exception as e:
        logger.error(f"Blocked User-Agent test error: {str(e)}")
        return False

def ensure_instance_running(instance_name, instance_id):
    """Ensure an AWS instance is running, start it if needed"""
    try:
        # Check instance state
        state = get_instance_state(instance_id)
        if state is None:
            logger.error(f"Could not determine state for {instance_name} instance {instance_id}")
            return False
            
        if state == "running":
            logger.info(f"{instance_name} instance {instance_id} is already running")
            return True
        elif state == "stopped":
            # Start the instance
            if not start_instance(instance_id):
                logger.error(f"Failed to start {instance_name} instance {instance_id}")
                return False
                
            # Wait for 120 seconds
            logger.info("Waiting 120 seconds for instance to start...")
            time.sleep(120)
            
            # Refresh Terraform state
            if not refresh_terraform_state():
                logger.warning("Failed to refresh Terraform state, continuing anyway...")
                
            return True
        else:
            logger.error(f"{instance_name} instance {instance_id} is in unexpected state: {state}")
            return False
    except Exception as e:
        logger.error(f"Error ensuring {instance_name} instance is running: {str(e)}")
        return False

def run_tests_for_instance(instance_name, ip):
    """Run all tests for a specific FortiWeb instance"""
    logger.info(f"Running tests for {instance_name} at {ip}")
    
    # Verify HTTP connectivity
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if not test_http_healthcheck(ip):
        logger.error(f"Health check failed for {instance_name}")
        return False
        
    # Test that requests with blocked User-Agent are rejected
    if not test_blocked_user_agent(ip):
        logger.error(f"Blocked User-Agent test failed for {instance_name}")
        return False
        
    logger.info(f"All tests passed for {instance_name}")
    return True
