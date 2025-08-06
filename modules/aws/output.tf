output "byol_instance_hostname" {
  description = "Private DNS name of the EC2 instance."
  value       = aws_instance.fortiweb_byol.id
}
output "fwb_byol_public_ip" {
  description = "Public IP address of fortiweb."
  value       = aws_instance.fortiweb_byol.public_ip
}

output "payg_instance_hostname" {
  description = "Private DNS name of the EC2 instance."
  value       = aws_instance.fortiweb_payg.id
}
output "fwb_payg_public_ip" {
  description = "Public IP address of fortiweb."
  value       = aws_instance.fortiweb_payg.public_ip
}
