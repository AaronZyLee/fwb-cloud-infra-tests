module "fortiweb_aws" {
  source        = "./modules/aws"
  region        = var.aws_region
  fwb_version   = var.fwb_version
  fwb_build     = var.fwb_build
  my_ip         = var.my_ip
  instance_type = var.aws_instance_type
  # pass other common inputs
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
}

module "fortiweb_oci" {
  source = "./modules/oci"
  region              = var.oci_region
  fwb_version         = var.fwb_version
  fwb_build           = var.fwb_build
  my_ip               = var.my_ip
  instance_type       = var.oci_instance_type
  compartment_id      = var.oci_compartment_id
  availability_domain = var.oci_availability_domain
  subnet_id           = var.oci_subnet_id
  # pass other common inputs
}
