variable "region" {
  description = "OCI region"
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
  description = "The compute instance's shape"
  type        = string
  default     = "VM.Standard2.1"
}

variable "compartment_id" {
  description = "OCI compartment ID"
  type        = string
}

variable "availability_domain" {
  description = "OCI availability domain"
  type        = string
}

variable "subnet_id" {
  description = "OCI subnet OCID"
  type        = string
}
