# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains infrastructure-as-code (IaC) configurations and automation scripts for deploying and testing FortiWeb cloud instances across multiple cloud providers (AWS, Azure, and OCI). The project uses Terraform for infrastructure provisioning and includes Python scripts for importing FortiWeb images and testing basic functionality.

## Key Components

1. **Terraform Modules**: Separate modules for AWS, Azure, and OCI cloud providers in the `modules/` directory
2. **Infrastructure Definitions**: Main Terraform files (`main.tf`, `variables.tf`, `output.tf`) defining resources for all providers
3. **Import Scripts**: Python scripts in `scripts/` directory for importing FortiWeb VM images to each cloud provider
4. **Testing Framework**: Basic functional tests in `tests/` directory for verifying deployed instances
5. **Configuration Templates**: Template files in `config/` directory for FortiWeb configuration

## Common Commands

### Infrastructure Deployment

```bash
# Initialize Terraform
terraform init

# Plan infrastructure deployment
terraform plan

# Apply infrastructure deployment
terraform apply

# Destroy infrastructure
terraform destroy
```

### Image Import

```bash
# Import FortiWeb image to AWS
python scripts/import-fwb-image-aws.py path/to/fwb-image.zip

# Import FortiWeb image to Azure
python scripts/import-fwb-image-azure.py path/to/fwb-image.zip

# Import FortiWeb image to OCI
python scripts/import-fwb-image-oci.py path/to/fwb-image.zip
```

### Testing

```bash
# Run basic traffic and attack tests for AWS
python tests/aws/basic_traffic_and_attack.py

# Run basic traffic and attack tests for Azure
python tests/azure/basic_traffic_and_attack.py
```

## Architecture Overview

### Core Structure

1. **Multi-Cloud Terraform Architecture**
   - Modular design with separate modules for each cloud provider (AWS, Azure, OCI)
   - Shared variables and outputs coordinated through root module
   - Provider-specific resources defined in respective module directories

2. **Image Import Pipeline**
   - Cloud-specific Python scripts for uploading VM images to object storage
   - Automated snapshot creation from uploaded images
   - AMI/Image creation with standardized tagging for version/build tracking

3. **Testing Framework**
   - Common utility library for shared testing functions
   - Provider-specific test implementations
   - Integration with Terraform outputs for dynamic instance configuration
   - Health checks and basic security validation tests

4. **Configuration Management**
   - Template-based FortiWeb configuration with variable substitution
   - Environment-specific settings managed through .env files
   - Dynamic configuration application via SSH

5. **Security and Networking**
   - Provider-specific security groups/network security groups with consistent rule sets
   - Restricted access based on user's public IP
   - Internal VPC/VNet/subnet communication enabled

## Development Notes

- Python scripts use cloud provider SDKs and require appropriate authentication setup
- Terraform state is managed locally (no remote backend configured)
- Environment variables are used for sensitive configuration values
- Tests depend on successful Terraform deployment and output availability