variable "location" {
  description = "Azure location"
  type        = string
}

variable "fwb_version" {
  description = "FortiWeb version tag for image filtering"
  type        = string
}

variable "fwb_build" {
  description = "FortiWeb build tag for image filtering"
  type        = string
}

variable "my_ip" {
  description = "My Public IP"
  type        = string
}

variable "instance_type" {
  description = "The VM instance's type"
  type        = string
}

variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
}

variable "storage_account_name" {
  description = "Azure storage account name"
  type        = string
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "virtual_network_name" {
  description = "Azure virtual network name"
  type        = string
}

variable "admin_username" {
  description = "Administrator username for the FortiWeb VM"
  type        = string
}

variable "admin_password" {
  description = "Administrator password for the FortiWeb VM"
  type        = string
}
