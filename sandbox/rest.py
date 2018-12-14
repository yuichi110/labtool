import json
import os
import random
import requests
import sys
import traceback
import pprint

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

class TestRestApi():                
  def __init__(self, ipAddress, username, password):    
    self.serverIpAddress = ipAddress
    self.username = username
    self.password = password
    self.index_url = 'https://{}:9440/'.format(self.serverIpAddress)
    self.v1_url = 'https://{}:9440/PrismGateway/services/rest/v1/'.format(self.serverIpAddress)
    self.v2_url = 'https://{}:9440/PrismGateway/services/rest/v2.0/'.format(self.serverIpAddress)
    self.session = self.get_server_session(self.username, self.password)

  def get_server_session(self, username, password):
    session = requests.Session()
    session.auth = (username, password)
    session.verify = False                                            
    session.headers.update(
        {'Content-Type': 'application/json; charset=utf-8'})
    return session

  def getClusterInformation(self):
    clusterURL = self.v1_url + "/cluster"
    serverResponse = self.session.get(clusterURL)
    return serverResponse.status_code, json.loads(serverResponse.text)

  def getNetworks(self):
    networkURL = self.v2_url + '/networks'
    serverResponse = self.session.get(networkURL)
    return serverResponse.status_code, json.loads(serverResponse.text)

  def getVms(self):
    vmURL = self.v2_url + '/vms/'
    serverResponse = self.session.get(vmURL)
    return serverResponse.status_code, json.loads(serverResponse.text)   

  def getVm(self, vm_uuid):
    vmURL = self.v2_url + '/vms/' + vm_uuid + '/disks'
    serverResponse = self.session.get(vmURL)
    return serverResponse.status_code, json.loads(serverResponse.text)  

  '''
  def createVm(self):
    payload = {
      'memory_mb':1024,
      'name':'test',
      'num_vcpus':1,
      'num_cores_per_vcpu':1,
      'vm_disks':[
      ]
    }
    json_payload = json.dumps(payload)
    vmCreateURL = self.v2_url + '/vms'
    serverResponse = self.session.post(vmCreateURL, data=json_payload)
    return serverResponse.status_code, json.loads(serverResponse.text)   
  '''

  def get_storagePoolId(self, name):
    serverResponse = self.session.get(self.v1_url + '/storage_pools')
    d = json.loads(serverResponse.text)

    for sp in d['entities']:
      if sp['name'] == name:
        return sp['id']

    raise 'Entity does not exist.'

  def get_container_uuid(self, name):
    serverResponse = self.session.get(self.v1_url + '/containers')
    d = json.loads(serverResponse.text)

    for cont in d['entities']:
      if cont['name'] == name:
        return cont['containerUuid']

    return ''

  def create_container(self, name, storagePoolId):
    payload = {
      "id": None,
      "name": name,
      "storagePoolId": storagePoolId,
      "totalExplicitReservedCapacity": 0,
      "advertisedCapacity": None,
      "compressionEnabled": True,
      "compressionDelayInSecs": 0,
      "fingerPrintOnWrite": "OFF",
      "onDiskDedup": "OFF"
    }
    json_payload = json.dumps(payload)
    serverResponse = self.session.post(self.v1_url + '/containers', data=json_payload)
    return serverResponse.status_code, json.loads(serverResponse.text)

  def get_images(self):
    serverResponse = self.session.get(self.v2_url + '/images')
    return json.loads(serverResponse.text)

  def create_image(self, image_name, file_url, container_uuid, image_type=None):
    if image_type is None:
      is_iso = file_url.lower().endswith('.iso')
      image_type = 'ISO_IMAGE' if is_iso else 'DISK_IMAGE'

    payload = {
      "name": image_name,
      "annotation": "",
      "imageType": image_type,
      "imageImportSpec": {
        "containerUuid": container_uuid,
        "url": file_url,
      }
    }

    json_payload = json.dumps(payload)
    print(json_payload)

    serverResponse = self.session.post(self.index_url + '/api/nutanix/v0.8/images', data=json_payload)
    return serverResponse.status_code, json.loads(serverResponse.text)


  def create_vm(self, name, memory_mb, num_vcpus, num_cores, image_name, network_name, ip_address, hypervisor):
    serverResponse = self.session.get(self.v2_url + '/images')
    d = json.loads(serverResponse.text)
    vmdisk_uuid = ''
    vmdisk_size = 0
    for image in d['entities']:
      if image['name'] == image_name:
        vmdisk_uuid = image['vm_disk_id']
        vmdisk_size = image['vm_disk_size']
        break

    serverResponse = self.session.get(self.v2_url + '/networks')
    d = json.loads(serverResponse.text)
    network_uuid = ''
    for network in d['entities']:
      if network['name'] == network_name:
        network_uuid = network['uuid']
        break

    payload = {
      "name": name,
      "memory_mb": memory_mb,
      "num_vcpus": num_vcpus,
      "description": "",
      "num_cores_per_vcpu": num_cores,
      "vm_disks": [
        {
          "is_cdrom": True,
          "is_empty": True,
          "disk_address": {
            "device_bus": "ide"
          }
        },
        {
          "is_cdrom": False,
          "disk_address": {
            "device_bus": "scsi"
          },
          "vm_disk_clone": {
            "disk_address": {
              "vmdisk_uuid": vmdisk_uuid
            },
            "minimum_size": vmdisk_size
          }
        }
      ],
      "vm_nics": [
        {
          "network_uuid": network_uuid,
          "requested_ip_address": ip_address
        }
      ],
      "hypervisor_type": hypervisor,
      "affinity": None,
      "vm_features": {
        "AGENT_VM": False
      }
    }

    json_payload = json.dumps(payload)
    print(json_payload)
    serverResponse = self.session.post(self.v2_url + '/vms?include_vm_disk_config=true&include_vm_nic_config=true', data=json_payload)
    return serverResponse.status_code, json.loads(serverResponse.text)



testRestApi = TestRestApi('10.149.160.41', 'admin', 'Nutanix/4u!')
#spid = testRestApi.get_storagePoolId('default-storage-pool-58446')
#testRestApi.create_container('container2', spid)
#container_uuid = testRestApi.get_container_uuid('container')
#testRestApi.create_image('centos7-iso2', 'nfs://10.149.245.50/Public/iso/linux/centos7_min.iso', container_uuid)
#testRestApi.create_vm('test-vm', 1024, 1, 1, 'IMG_CENT7_MIN', 'vlan168', '10.149.168.52', 'ACROPOLIS')

status, data = testRestApi.getClusterInformation()
print(json.dumps(data, indent=2))

#print(container_uuid)

'''
Create VM

{
  "name": "test",
  "memory_mb": 1024,
  "num_vcpus": 1,
  "description": "",
  "num_cores_per_vcpu": 1,
  "vm_disks": [
    {
      "is_cdrom": true,
      "is_empty": true,
      "disk_address": {
        "device_bus": "ide"
      }
    },
    {
      "is_cdrom": false,
      "disk_address": {
        "device_bus": "scsi"
      },
      "vm_disk_clone": {
        "disk_address": {
          "vmdisk_uuid": "fd16c5b2-02b8-48bb-bec3-07d0c04b1a10"
        },
        "minimum_size": 21474836480
      }
    }
  ],
  "vm_nics": [
    {
      "network_uuid": "c101b7e5-90ea-43db-886d-a72455cc5031",
      "requested_ip_address": "10.149.169.54"
    }
  ],
  "hypervisor_type": "ACROPOLIS",
  "affinity": null,
  "vm_features": {
    "AGENT_VM": false
  }
}


{
  "name": "CentOS7",
  "memory_mb": 1024,
  "num_vcpus": 1,
  "description": "",
  "num_cores_per_vcpu": 1,
  "vm_disks": [
    {
      "is_cdrom": true,
      "is_empty": false,
      "disk_address": {
        "device_bus": "ide"
      },
      "vm_disk_clone": {
        "disk_address": {
          "vmdisk_uuid": "6481c856-ac12-4eb4-a5b7-bb18f41ee9ae"
        },
        "minimum_size": 944892805.12
      }
    },
    {
      "is_cdrom": false,
      "disk_address": {
        "device_bus": "scsi"
      },
      "vm_disk_create": {
        "storage_container_uuid": "146ea8b1-3252-4992-a836-a2e7822bbb61",
        "size": 21474836480
      }
    }
  ],
  "vm_nics": [
    {
      "network_uuid": "2ce7f701-7168-4640-801e-24715db69863",
      "requested_ip_address": "10.149.168.50"
    }
  ],
  "hypervisor_type": "ACROPOLIS",
  "affinity": null,
  "vm_features": {
    "AGENT_VM": false
  }
}


Create Container
{
  "id": null,
  "name": "container",
  "storagePoolId": "00057ce0-374c-bde1-0000-00000000e44e::10",
  "totalExplicitReservedCapacity": 0,
  "advertisedCapacity": null,
  "compressionEnabled": true,
  "compressionDelayInSecs": 0,
  "fingerPrintOnWrite": "OFF",
  "onDiskDedup": "OFF"
}

Create Image
{
  "name": "ISO-CENT7-MIN",
  "annotation": "",
  "imageType": "ISO_IMAGE",
  "imageImportSpec": {
    "containerUuid": "146ea8b1-3252-4992-a836-a2e7822bbb61",
    "url": "nfs://10.149.245.50/Public/iso/linux/centos7_min.iso"
  }
}


Create Network
{
  "name": "vlan168",
  "vlanId": "168",
  "ipConfig": {
    "dhcpOptions": {
      "domainNameServers": "8.8.8.8"
    },
    "networkAddress": "10.149.168.0",
    "prefixLength": "24",
    "defaultGateway": "10.149.168.1",
    "pool": [
      {
        "range": "10.149.168.50 10.149.168.99"
      }
    ]
  }
}


https://10.149.160.41:9440/PrismGateway/services/rest/v2.0/vms?include_vm_disk_config=true&include_vm_nic_config=true
{
  "name": "VM-00",
  "memory_mb": 1024,
  "num_vcpus": 1,
  "description": "",
  "num_cores_per_vcpu": 1,
  "vm_disks": [
    {
      "is_cdrom": true,
      "is_empty": true,
      "disk_address": {
        "device_bus": "ide"
      }
    },
    {
      "is_cdrom": false,
      "disk_address": {
        "device_bus": "scsi"
      },
      "vm_disk_clone": {
        "disk_address": {
          "vmdisk_uuid": "0e680d11-29b3-4e94-b901-c7130a589b62"
        },
        "minimum_size": 21474836480
      }
    }
  ],
  "vm_nics": [
    {
      "network_uuid": "2ce7f701-7168-4640-801e-24715db69863",
      "requested_ip_address": "10.149.168.51"
    }
  ],
  "hypervisor_type": "ACROPOLIS",
  "affinity": null,
  "vm_features": {
    "AGENT_VM": false
  }
}
'''