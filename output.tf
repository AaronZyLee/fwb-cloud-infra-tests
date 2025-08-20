# aws
output "aws_byol_instance_hostname" {
  description = "AWS Private DNS name of the EC2 instance."
  value       = length(module.fortiweb_aws) > 0 ? module.fortiweb_aws[0].byol_instance_hostname : null
}

output "fwb_aws_byol_public_ip" {
  description = "AWS Public IP address of fortiweb."
  value       = length(module.fortiweb_aws) > 0 ? module.fortiweb_aws[0].fwb_byol_public_ip : null
}

output "aws_payg_instance_hostname" {
  description = "AWS Private DNS name of the EC2 instance."
  value       = length(module.fortiweb_aws) > 0 ? module.fortiweb_aws[0].payg_instance_hostname : null
}

output "fwb_aws_payg_public_ip" {
  description = "AWS Public IP address of fortiweb."
  value       = length(module.fortiweb_aws) > 0 ? module.fortiweb_aws[0].fwb_payg_public_ip : null
}

# azure
output "azure_byol_instance_hostname" {
  description = "Azure Private DNS name of the VM instance."
  value       = length(module.fortiweb_azure) > 0 ? module.fortiweb_azure[0].byol_instance_hostname : null
}

output "fwb_azure_byol_public_ip" {
  description = "Azure Public IP address of fortiweb."
  value       = length(module.fortiweb_azure) > 0 ? module.fortiweb_azure[0].fwb_byol_public_ip : null
}

output "azure_payg_instance_hostname" {
  description = "Azure Private DNS name of the VM instance."
  value       = length(module.fortiweb_azure) > 0 ? module.fortiweb_azure[0].payg_instance_hostname : null
}

output "fwb_azure_payg_public_ip" {
  description = "Azure Public IP address of fortiweb."
  value       = length(module.fortiweb_azure) > 0 ? module.fortiweb_azure[0].fwb_payg_public_ip : null
}

# oci
output "oci_byol_instance_hostname" {
  description = "OCI OCID of the compute instance."
  value       = length(module.fortiweb_oci) > 0 ? module.fortiweb_oci[0].byol_instance_hostname : null
}

output "fwb_oci_byol_public_ip" {
  description = "OCI Public IP address of fortiweb."
  value       = length(module.fortiweb_oci) > 0 ? module.fortiweb_oci[0].fwb_byol_public_ip : null
}
