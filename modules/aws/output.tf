output "byol_instance_hostname" {
  description = "Private DNS name of the EC2 instance."
  value       = length(aws_instance.fortiweb_byol) > 0 ? aws_instance.fortiweb_byol[0].id : null
}
output "fwb_byol_public_ip" {
  description = "Public IP address of fortiweb."
  value       = length(aws_instance.fortiweb_byol) > 0 ? aws_instance.fortiweb_byol[0].public_ip : null
}

output "payg_instance_hostname" {
  description = "Private DNS name of the EC2 instance."
  value       = length(aws_instance.fortiweb_payg) > 0 ? aws_instance.fortiweb_payg[0].id : null
}
output "fwb_payg_public_ip" {
  description = "Public IP address of fortiweb."
  value       = length(aws_instance.fortiweb_payg) > 0 ? aws_instance.fortiweb_payg[0].public_ip : null
}
