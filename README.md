# FWB Cloud Infrastructure

This repository contains Terraform configurations to deploy FortiWeb instances across multiple cloud providers (AWS, Azure, and OCI).

## Workspaces

This project uses Terraform workspaces to isolate deployments for different cloud providers:

- `default` - Deploys to all cloud providers simultaneously
- `aws` - Deploys only to AWS
- `azure` - Deploys only to Azure
- `oci` - Deploys only to OCI

## Usage

1. Initialize Terraform:
   ```bash
   terraform init
   ```

2. Select the appropriate workspace:
   ```bash
   # For deploying to all clouds
   terraform workspace select default
   
   # For deploying only to OCI
   terraform workspace select oci
   
   # For deploying only to AWS
   terraform workspace select aws
   
   # For deploying only to Azure
   terraform workspace select azure
   ```

3. Apply the configuration:
   ```bash
   terraform apply
   ```

## Prerequisites

- Terraform >= 1.2
- Appropriate cloud provider credentials configured

## Configuration

Edit `terraform.tfvars` to configure your deployment settings.
