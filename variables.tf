#Common
variable "my_ip" {
  description = "My Public IP"
}

variable "fwb_version" {
  description = "FortiWeb version tag for AMI filtering"
  type        = string
}

variable "fwb_build" {
  description = "FortiWeb build tag for AMI filtering"
  type        = string
}

#AWS
variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "aws_instance_type" {
  description = "The EC2 instance's type."
  type        = string
  default     = "t3.micro"
}

#Azure
variable "azure_instance_type" {
  description = "The Azure VM instance's type."
  type        = string
  default     = "Standard_B1ms"
}

variable "azure_subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "azure_location" {
  description = "Azure location"
  type        = string
}

variable "azure_resource_group_name" {
  description = "Azure resource group name"
  type        = string
}

variable "azure_storage_account_name" {
  description = "Azure storage account name"
  type        = string
}

variable "azure_virtual_network_name" {
  description = "Azure virtual network name"
  type        = string
}

variable "azure_admin_username" {
  description = "Administrator username for the Azure FortiWeb VM"
  type        = string
}

variable "azure_admin_password" {
  description = "Administrator password for the Azure FortiWeb VM"
  type        = string
}

# OCI
variable "oci_instance_type" {
  description = "The OCI compute instance's shape."
  type        = string
  default     = "VM.Standard2.1"
}

variable "oci_instance_ocpus" {
  description = "Number of OCPUs for Flex instances"
  type        = number
  default     = 1
}

variable "oci_instance_memory_in_gbs" {
  description = "Memory in GBs for Flex instances"
  type        = number
  default     = 16
}

variable "oci_compartment_id" {
  description = "OCI compartment ID"
  type        = string
}

variable "oci_availability_domain" {
  description = "OCI availability domain"
  type        = string
}

variable "oci_subnet_id" {
  description = "OCI subnet OCID"
  type        = string
}

variable "oci_region" {
  description = "OCI region"
  type        = string
}
