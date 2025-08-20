@echo off
REM Demo script for using Terraform workspaces with FWB Cloud Infrastructure

echo === FWB Cloud Infrastructure Workspace Demo ===

echo 1. Initializing Terraform...
terraform init

echo 2. Listing available workspaces...
terraform workspace list

echo 3. Selecting OCI workspace...
terraform workspace select oci

echo 4. Showing current workspace...
terraform workspace show

echo 5. Planning deployment (OCI only)...
terraform plan

echo 6. To deploy to OCI only, run: terraform apply

echo.
echo To switch to other workspaces:
echo   terraform workspace select aws     # Deploy to AWS only
echo   terraform workspace select azure   # Deploy to Azure only
echo   terraform workspace select default # Deploy to all clouds
