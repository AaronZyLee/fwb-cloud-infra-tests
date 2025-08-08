terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.92.0"
    }
  }
}

provider "aws" {
  region = var.region
}

data "aws_vpc" "default" {
  default = true
}

data "aws_ami" "fortiweb_payg_ami" {
  most_recent = true
  filter {
    name   = "tag:owner"
    values = ["fwbqa"]
  }
  filter {
    name   = "tag:version"
    values = [var.fwb_version]
  }
  filter {
    name   = "tag:build"
    values = [var.fwb_build]
  }
  filter {
    name   = "tag:license_type"
    values = ["payg"]
  }
  owners = ["self"]
}

data "aws_ami" "fortiweb_byol_ami" {
  most_recent = true
  filter {
    name   = "tag:owner"
    values = ["fwbqa"]
  }
  filter {
    name   = "tag:version"
    values = [var.fwb_version]
  }
  filter {
    name   = "tag:build"
    values = [var.fwb_build]
  }
  filter {
    name   = "tag:license_type"
    values = ["byol"]
  }
  owners = ["self"]
}


resource "aws_security_group" "fortiweb_sg" {
  name        = "fortiweb-qa-sg-lzeyu"
  description = "Allow basic traffic for FortiWeb"
  vpc_id      = data.aws_vpc.default.id # 👈 Use default VPC

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "Allow HTTPS"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "Allow HTTP"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "Allow HTTPS"
  }

  ingress {
    from_port   = 8443
    to_port     = 8443
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "Allow FWB GUI Management"
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
    description = "Allow SSH"
  }

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [data.aws_vpc.default.cidr_block]
    description = "Allow all traffic within VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name  = "fortiweb-qa-sg-lzeyu"
    Owner = "lzeyu"
  }
}


resource "aws_instance" "fortiweb_payg" {
  ami                    = data.aws_ami.fortiweb_payg_ami.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.fortiweb_sg.id]
  root_block_device {
    volume_size           = 2
    volume_type           = "gp3"
    delete_on_termination = true
  }
  ebs_block_device {
    device_name           = "/dev/sdb"
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
  }
  tags = {
    Name  = "fwb-payg-${var.fwb_version}-${var.fwb_build}"
    Owner = "fwbqa"
  }
}

resource "aws_instance" "fortiweb_byol" {
  ami                    = data.aws_ami.fortiweb_byol_ami.id
  instance_type          = var.instance_type
  vpc_security_group_ids = [aws_security_group.fortiweb_sg.id]
  root_block_device {
    volume_size           = 8
    volume_type           = "gp3"
    delete_on_termination = true
  }
  ebs_block_device {
    device_name           = "/dev/sdb"
    volume_size           = 30
    volume_type           = "gp3"
    delete_on_termination = true
  }
  tags = {
    Name  = "fwb-byol-${var.fwb_version}-${var.fwb_build}"
    Owner = "fwbqa"
  }
}
