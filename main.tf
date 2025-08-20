# Provider configurations
provider "aws" {
  region = var.aws_region
}

provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
}

provider "oci" {
  region = var.oci_region
}

# Use terraform.workspace to conditionally deploy modules based on the current workspace
# Default workspace will deploy all modules, specific cloud workspaces will deploy only that cloud's module

module "fortiweb_aws" {
  source        = "./modules/aws"
  region        = var.aws_region
  fwb_version   = var.fwb_version
  fwb_build     = var.fwb_build
  my_ip         = var.my_ip
  instance_type = var.aws_instance_type
  # pass other common inputs

  providers = {
    aws = aws
  }

  count = terraform.workspace == "default" || terraform.workspace == "aws" ? 1 : 0
}

module "fortiweb_azure" {
  source               = "./modules/azure"
  location             = var.azure_location
  fwb_version          = var.fwb_version
  fwb_build            = var.fwb_build
  my_ip                = var.my_ip
  instance_type        = var.azure_instance_type
  resource_group_name  = var.azure_resource_group_name
  storage_account_name = var.azure_storage_account_name
  subscription_id      = var.azure_subscription_id
  virtual_network_name = var.azure_virtual_network_name
  admin_username       = var.azure_admin_username
  admin_password       = var.azure_admin_password
  # pass other common inputs

  providers = {
    azurerm = azurerm
  }

  count = terraform.workspace == "default" || terraform.workspace == "azure" ? 1 : 0
}

module "fortiweb_oci" {
  source                 = "./modules/oci"
  region                 = var.oci_region
  fwb_version            = var.fwb_version
  fwb_build              = var.fwb_build
  my_ip                  = var.my_ip
  instance_type          = var.oci_instance_type
  instance_ocpus         = var.oci_instance_ocpus
  instance_memory_in_gbs = var.oci_instance_memory_in_gbs
  compartment_id         = var.oci_compartment_id
  availability_domain    = var.oci_availability_domain
  subnet_id              = var.oci_subnet_id
  # pass other common inputs

  providers = {
    oci = oci
  }

  count = terraform.workspace == "default" || terraform.workspace == "oci" ? 1 : 0
}
