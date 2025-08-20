terraform {
  required_providers {
    oci = {
      source  = "oracle/oci"
      version = "~> 7.14.0"  # Updated to a more recent version
    }
  }
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

locals {
  ad_name = data.oci_identity_availability_domains.ads.availability_domains[0].name
}

data "oci_core_images" "fortiweb_byol_images" {
  compartment_id = var.compartment_id
  display_name   = "fwb-byol-${var.fwb_version}-${var.fwb_build}"
  sort_by        = "TIMECREATED"
  sort_order     = "DESC"
}

data "oci_core_subnet" "default" {
  subnet_id = var.subnet_id
}


resource "oci_core_network_security_group" "fortiweb_nsg" {
  compartment_id = var.compartment_id
  vcn_id         = data.oci_core_subnet.default.vcn_id
  display_name   = "fortiweb-qa-nsg-lzeyu"
}

resource "oci_core_network_security_group_security_rule" "allow_https" {
  network_security_group_id = oci_core_network_security_group.fortiweb_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = var.my_ip
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = 443
      max = 443
    }
  }
  description = "Allow HTTPS"
}

resource "oci_core_network_security_group_security_rule" "allow_http" {
  network_security_group_id = oci_core_network_security_group.fortiweb_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = var.my_ip
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = 80
      max = 80
    }
  }
  description = "Allow HTTP"
}

resource "oci_core_network_security_group_security_rule" "allow_fwb_gui" {
  network_security_group_id = oci_core_network_security_group.fortiweb_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = var.my_ip
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = 8443
      max = 8443
    }
  }
  description = "Allow FWB GUI Management"
}

resource "oci_core_network_security_group_security_rule" "allow_ssh" {
  network_security_group_id = oci_core_network_security_group.fortiweb_nsg.id
  direction                 = "INGRESS"
  protocol                  = "6" # TCP
  source                    = var.my_ip
  source_type               = "CIDR_BLOCK"
  tcp_options {
    destination_port_range {
      min = 22
      max = 22
    }
  }
  description = "Allow SSH"
}

resource "oci_core_network_security_group_security_rule" "allow_vpc_internal" {
  network_security_group_id = oci_core_network_security_group.fortiweb_nsg.id
  direction                 = "INGRESS"
  protocol                  = "all"
  source                    = data.oci_core_subnet.default.cidr_block
  source_type               = "CIDR_BLOCK"
  description               = "Allow all traffic within VCN"
}

resource "oci_core_instance" "fortiweb_byol" {
  availability_domain = local.ad_name
  compartment_id      = var.compartment_id
  display_name        = "fwb-byol-${var.fwb_version}-${var.fwb_build}"
  shape               = var.instance_type

  shape_config {
    ocpus         = var.instance_ocpus
    memory_in_gbs = var.instance_memory_in_gbs
  }

  create_vnic_details {
    assign_public_ip = true
    subnet_id        = var.subnet_id
    nsg_ids          = [oci_core_network_security_group.fortiweb_nsg.id]
  }

  source_details {
    source_type = "image"
    source_id   = data.oci_core_images.fortiweb_byol_images.images[0]["id"]
  }

  freeform_tags = {
    "Name"  = "fwb-byol-${var.fwb_version}-${var.fwb_build}"
    "Owner" = "fwbqa"
  }
}
