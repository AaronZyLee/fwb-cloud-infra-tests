terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.37.0"
    }
    oci = {
      source  = "oracle/oci"
      version = "~> 7.11.0"
    }
  }

  required_version = ">= 1.2"
}
