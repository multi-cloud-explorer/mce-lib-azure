# Cloud Explorer - Azure

Librairie pour télécharger un inventaire des ressources d'une souscription Azure.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Build Status](https://travis-ci.org/multi-cloud-explorer/mce-lib-azure.svg)](https://travis-ci.org/multi-cloud-explorer/mce-lib-azure)
[![Coverage Status](https://coveralls.io/repos/github/multi-cloud-explorer/mce-lib-azure/badge.svg?branch=master)](https://coveralls.io/github/multi-cloud-explorer/mce-lib-azure?branch=master)
[![Code Health](https://landscape.io/github/multi-cloud-explorer/mce-lib-azure/master/landscape.svg?style=flat)](https://landscape.io/github/multi-cloud-explorer/mce-lib-azure/master)
[![Requirements Status](https://requires.io/github/multi-cloud-explorer/mce-lib-azure/requirements.svg?branch=master)](https://requires.io/github/multi-cloud-explorer/mce-lib-azure/requirements/?branch=master)

[Documentation](https://multi-cloud-explorer.readthedocs.org)

## Installation

```shell
git clone https://github.com/multi-cloud-explorer/mce-lib-azure.git
cd mce-lib-azure
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install .
```

## Configure

```shell
export MCE_AZURE_SUBSCRIPTION='00000000-0000-0000-0000-000000000000'    
export MCE_AZURE_TENANT='00000000-0000-0000-0000-000000000000'
export MCE_AZURE_USER='CHANGE_ME'
export MCE_AZURE_PASSWORD='CHANGE_ME'
```

## Get a light version of all resources in subscription

```shell
mce-az -C list --json --export resources-list.json
```

```json
[
    {
        "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/Cloud-Shell/providers/Microsoft.Storage/storageAccounts/xxxcloudshellsa01",
        "name": "xxxcloudshellsa01",
        "type": "Microsoft.Storage/storageAccounts",
        "sku": {
            "name": "Standard_LRS",
            "tier": "Standard"
        },
        "kind": "Storage",
        "location": "westeurope",
        "tags": {
            "ms-resource-usage": "azure-cloud-shell"
        }
    },
    {
        "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/xxx-CSP-Reporting-01/providers/Microsoft.Automation/automationAccounts/xxx-
csp-reporting-autoaccount",
        "name": "xxx-csp-reporting-autoaccount",
        "type": "Microsoft.Automation/automationAccounts",
        "location": "westeurope",
        "tags": {}
    }
]
```

> Add --expand parameter for full version (warning: is long time)

```shell
mce-az -C list --json --expand --export resources-list-expand.json
```

## Get list of Resource Group

```shell
mce-az -C group --json
```

```json
[
    {
        "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MY_RG",
        "name": "MY_RG",
        "location": "francecentral",
        "tags": {},
        "properties": {
            "provisioningState": "Succeeded"
        }
    },
    {
        "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/Cloud-Shell",
        "name": "Cloud-Shell",
        "location": "westeurope",
        "properties": {
            "provisioningState": "Succeeded"
        }
    }
]
```

## Get resource by ID

```shell
mce-az --json -C get \
  -a /subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MY_RG_GROUP/providers/Microsoft.Compute/virtualMachines/MY_VM
```

```json
{
    "name": "MY_VM",
    "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MY_RG_GROUP/providers/Microsoft.Compute/virtualMachines/MY_VM",
    "type": "Microsoft.Compute/virtualMachines",
    "location": "westeurope",
    "tags": {
        "hidden-DevTestLabs-LabUId": "00000000-0000-0000-0000-000000000000",
        "hidden-DevTestLabs-LogicalResourceUId": "00000000-0000-0000-0000-000000000000"
    },
    "properties": {
        "vmId": "00000000-0000-0000-0000-000000000000",
        "hardwareProfile": {
            "vmSize": "Standard_D2s_v3"
        },
        "storageProfile": {
            "imageReference": {
                "publisher": "MicrosoftWindowsServer",
                "offer": "WindowsServer",
                "sku": "2012-Datacenter-smalldisk",
                "version": "latest"
            },
            "osDisk": {
                "osType": "Windows",
                "name": "MY_VM",
                "createOption": "FromImage",
                "caching": "ReadWrite",
                "managedDisk": {
                    "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MY_RG_GROUP/providers/Microsoft.Compute/disks/MY_VM"
                }
            },
            "dataDisks": []
        },
        "osProfile": {
            "computerName": "MY_VM",
            "adminUsername": "gitlab-runner",
            "windowsConfiguration": {
                "provisionVMAgent": true,
                "enableAutomaticUpdates": true
            },
            "secrets": [],
            "allowExtensionOperations": true
        },
        "networkProfile": {
            "networkInterfaces": [
                {
                    "id": "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/MY_RG_GROUP/providers/Microsoft.Network/networkInterfaces/MY_NETWORK"
                }
            ]
        },
        "provisioningState": "Succeeded"
    }
}
```

## Update and use providers file

```shell
mce-az-providers --output /tmp/azure-providers.json

export MCE_PROVIDERS_FILEPATH/tmp/azure-providers.json
```
