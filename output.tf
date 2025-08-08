# aws
output "aws_byol_instance_hostname" {
  description = "AWS Private DNS name of the EC2 instance."
  value       = module.fortiweb_aws.byol_instance_hostname
}

output "fwb_aws_byol_public_ip" {
  description = "AWS Public IP address of fortiweb."
  value       = module.fortiweb_aws.fwb_byol_public_ip
}

output "aws_payg_instance_hostname" {
  description = "AWS Private DNS name of the EC2 instance."
  value       = module.fortiweb_aws.payg_instance_hostname
}

output "fwb_aws_payg_public_ip" {
  description = "AWS Public IP address of fortiweb."
  value       = module.fortiweb_aws.fwb_payg_public_ip
}

# azure
output "azure_byol_instance_hostname" {
  description = "Azure Private DNS name of the VM instance."
  value       = module.fortiweb_azure.byol_instance_hostname
}

output "fwb_azure_byol_public_ip" {
  description = "Azure Public IP address of fortiweb."
  value       = module.fortiweb_azure.fwb_byol_public_ip
}

output "azure_payg_instance_hostname" {
  description = "Azure Private DNS name of the VM instance."
  value       = module.fortiweb_azure.payg_instance_hostname
}

output "fwb_azure_payg_public_ip" {
  description = "Azure Public IP address of fortiweb."
  value       = module.fortiweb_azure.fwb_payg_public_ip
}

# oci
# output "oci_byol_instance_hostname" {
#   description = "OCI OCID of the compute instance."
#   value       = module.fortiweb_oci.byol_instance_hostname
# }

# output "fwb_oci_byol_public_ip" {
#   description = "OCI Public IP address of fortiweb."
#   value       = module.fortiweb_oci.fwb_byol_public_ip
# }
