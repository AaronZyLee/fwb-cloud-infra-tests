variable "region" {
  description = "AWS region"
  type        = string
}

variable "fwb_version" {
  description = "FortiWeb version tag for AMI filtering"
  type        = string
}

variable "fwb_build" {
  description = "FortiWeb build tag for AMI filtering"
  type        = string
}

variable "my_ip" {
  description = "My Public IP"
  type        = string
}

variable "instance_type" {
  description = "The EC2 instance's type"
  type        = string
}
