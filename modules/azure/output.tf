output "byol_instance_hostname" {
  description = "Private DNS name of the VM instance."
  value       = azurerm_linux_virtual_machine.fortiweb_byol.id
}

output "fwb_byol_public_ip" {
  description = "Public IP address of fortiweb."
  value       = azurerm_public_ip.fortiweb_byol.ip_address
}

output "payg_instance_hostname" {
  description = "Private DNS name of the VM instance."
  value       = azurerm_linux_virtual_machine.fortiweb_payg.id
}

output "fwb_payg_public_ip" {
  description = "Public IP address of fortiweb."
  value       = azurerm_public_ip.fortiweb_payg.ip_address
}
