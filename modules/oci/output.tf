output "byol_instance_hostname" {
  description = "OCID of the compute instance."
  value       = oci_core_instance.fortiweb_byol.id
}

output "fwb_byol_public_ip" {
  description = "Public IP address of fortiweb."
  value       = oci_core_instance.fortiweb_byol.*.private_ip
}
