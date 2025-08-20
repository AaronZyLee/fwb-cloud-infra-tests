terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "4.37.0"
    }
  }
}

data "azurerm_resource_group" "main" {
  name = var.resource_group_name
}

data "azurerm_virtual_network" "default" {
  name                = var.virtual_network_name
  resource_group_name = var.resource_group_name
}

data "azurerm_subnet" "default" {
  name                 = "default"
  virtual_network_name = data.azurerm_virtual_network.default.name
  resource_group_name  = var.resource_group_name
}

data "azurerm_image" "fortiweb_payg_image" {
  name                = "fwb-payg-${var.fwb_version}-${var.fwb_build}"
  resource_group_name = var.resource_group_name
}

data "azurerm_image" "fortiweb_byol_image" {
  name                = "fwb-byol-${var.fwb_version}-${var.fwb_build}"
  resource_group_name = var.resource_group_name
}

resource "azurerm_network_security_group" "fortiweb_nsg" {
  name                = "fortiweb-qa-nsg-lzeyu"
  location            = var.location
  resource_group_name = var.resource_group_name

  security_rule {
    name                       = "AllowHTTPS"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = var.my_ip
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowHTTP"
    priority                   = 1002
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = var.my_ip
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowFWBGUI"
    priority                   = 1003
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8443"
    source_address_prefix      = var.my_ip
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowSSH"
    priority                   = 1004
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = var.my_ip
    destination_address_prefix = "*"
  }

  security_rule {
    name                       = "AllowVPCInternal"
    priority                   = 1005
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = data.azurerm_virtual_network.default.address_space[0]
    destination_address_prefix = "*"
  }

  tags = {
    Name  = "fortiweb-qa-nsg-lzeyu"
    Owner = "lzeyu"
  }
}

resource "azurerm_network_interface" "fortiweb_payg_nic" {
  name                = "fortiweb-payg-nic"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = data.azurerm_subnet.default.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.fortiweb_payg.id
  }
}

resource "azurerm_network_interface" "fortiweb_byol_nic" {
  name                = "fortiweb-byol-nic"
  location            = var.location
  resource_group_name = var.resource_group_name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = data.azurerm_subnet.default.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.fortiweb_byol.id
  }
}

resource "azurerm_public_ip" "fortiweb_payg" {
  name                = "fortiweb-payg-ip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
}

resource "azurerm_public_ip" "fortiweb_byol" {
  name                = "fortiweb-byol-ip"
  location            = var.location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
}



resource "azurerm_virtual_machine" "fortiweb_payg" {
  name                             = "fwb-payg-${var.fwb_version}-${var.fwb_build}"
  location                         = var.location
  resource_group_name              = var.resource_group_name
  network_interface_ids            = [azurerm_network_interface.fortiweb_payg_nic.id]
  vm_size                          = var.instance_type
  delete_os_disk_on_termination    = true
  delete_data_disks_on_termination = true

  storage_image_reference {
    id = data.azurerm_image.fortiweb_payg_image.id
  }

  storage_os_disk {
    name              = "fwb-payg-os-disk"
    caching           = "None"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }

  storage_data_disk {
    name              = "fwb-payg-data-disk"
    managed_disk_type = "Premium_LRS"
    create_option     = "Empty"
    caching           = "ReadOnly"
    disk_size_gb      = 32
    lun               = 0
  }

  os_profile {
    computer_name  = "fwb-payg"
    admin_username = var.admin_username
    admin_password = var.admin_password
  }

  os_profile_linux_config {
    disable_password_authentication = false
  }

  tags = {
    Name  = "fwb-payg-${var.fwb_version}-${var.fwb_build}"
    Owner = "fwbqa"
  }
}



resource "azurerm_virtual_machine" "fortiweb_byol" {
  name                             = "fwb-byol-${var.fwb_version}-${var.fwb_build}"
  location                         = var.location
  resource_group_name              = var.resource_group_name
  network_interface_ids            = [azurerm_network_interface.fortiweb_byol_nic.id]
  vm_size                          = var.instance_type
  delete_os_disk_on_termination    = true
  delete_data_disks_on_termination = true

  storage_image_reference {
    id = data.azurerm_image.fortiweb_byol_image.id
  }

  storage_os_disk {
    name              = "fwb-byol-os-disk"
    caching           = "None"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }

  storage_data_disk {
    name              = "fwb-byol-data-disk"
    managed_disk_type = "Premium_LRS"
    create_option     = "Empty"
    caching           = "ReadOnly"
    disk_size_gb      = 32
    lun               = 0
  }

  os_profile {
    computer_name  = "fwb-byol"
    admin_username = var.admin_username
    admin_password = var.admin_password
  }

  os_profile_linux_config {
    disable_password_authentication = false
  }

  tags = {
    Name  = "fwb-byol-${var.fwb_version}-${var.fwb_build}"
    Owner = "fwbqa"
  }
}


resource "azurerm_network_interface_security_group_association" "fortiweb_payg_nsg_association" {
  network_interface_id      = azurerm_network_interface.fortiweb_payg_nic.id
  network_security_group_id = azurerm_network_security_group.fortiweb_nsg.id
}

resource "azurerm_network_interface_security_group_association" "fortiweb_byol_nsg_association" {
  network_interface_id      = azurerm_network_interface.fortiweb_byol_nic.id
  network_security_group_id = azurerm_network_security_group.fortiweb_nsg.id
}
