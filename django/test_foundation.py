from nutanix_foundation import SetupOps
import json

cluster = json.loads('''{
    "name": "poc02",
    "description": "POC02",
    "foundation_vms": {
      "ip_addresses": [
        "10.149.0.5"
      ],
      "user": "nutanix",
      "password": "nutanix/4u",
      "nos_packages": {
        "5.10.2": "nutanix_installer_package-release-euphrates-5.10.2-stable.tar"
      }
    },
    "basics": {
      "language": "ja-JP",
      "nfs_whitelists": [
        "10.0.0.0,255.0.0.0"
      ]
    },
    "containers": [
      "container",
      "NutanixManagementShare"
    ],
    "networks": {
      "net_10.149.0.0/17": {
        "use_dhcp": true,
        "vlan": 0,
        "network": "10.149.0.0",
        "prefix": 17,
        "gateway": "10.149.0.1",
        "dns": "8.8.8.8",
        "pools": [
          {
            "from": "10.149.2.101",
            "to": "10.149.2.250"
          }
        ]
      }
    },
    "images": {
      "virtio_1.1.3": {
        "container": "container",
        "url": "nfs://10.149.245.50/Public/labtool/iso/virtio_1.1.3.iso"
      },
      "iso_cent6_min": {
        "container": "container",
        "url": "nfs://10.149.245.50/Public/labtool/iso/centos6_min.iso"
      },
      "iso_cent7_min": {
        "container": "container",
        "url": "nfs://10.149.245.50/Public/labtool/iso/centos7_min.iso"
      },
      "iso_win2012r2_eng": {
        "container": "container",
        "url": "nfs://10.149.245.50/Public/labtool/iso/winserv2012r2_eng.iso"
      },
      "img_foundation_4.3.1": {
        "container": "container",
        "url": "nfs://10.149.245.50/Public/labtool/foundationvm/Foundation_VM-4.3.1-disk-0.qcow2"
      },
      "img_centos7_eng": {
        "container": "container",
        "url": "nfs://10.149.245.50/Public/labtool/image/centos7_eng_raw"
      },
      "img_win2012r2_eng": {
        "container": "container",
        "url": "nfs://10.149.245.50/Public/labtool/image/win2012r2_eng_raw"
      }
    },
    "uuid": "6d895df4-2676-48a3-bf8c-a72ca398c4c4",
    "POCID": "2",
    "external_ip": "10.149.2.41",
    "netmask": "255.255.128.0",
    "gateway": "10.149.0.1",
    "ntp_server": "ntp.nict.jp",
    "name_server": "8.8.8.8",
    "prism_user": "admin",
    "prism_password": "Nutanix/4u!",
    "nodes": [
      {
        "host_name": "AHV-1",
        "position": "A",
        "ipmi_mac": "00:25:90:d6:05:24",
        "ipmi_ip": "10.149.2.11",
        "host_ip": "10.149.2.21",
        "cvm_ip": "10.149.2.31"
      },
      {
        "host_name": "AHV-2",
        "position": "B",
        "ipmi_mac": "00:25:90:d6:05:9e",
        "ipmi_ip": "10.149.2.12",
        "host_ip": "10.149.2.22",
        "cvm_ip": "10.149.2.32"
      },
      {
        "host_name": "AHV-3",
        "position": "C",
        "ipmi_mac": "00:25:90:d6:05:26",
        "ipmi_ip": "10.149.2.13",
        "host_ip": "10.149.2.23",
        "cvm_ip": "10.149.2.33"
      },
      {
        "host_name": "AHV-4",
        "position": "D",
        "ipmi_mac": "0c:c4:7a:45:e3:c4",
        "ipmi_ip": "10.149.2.14",
        "host_ip": "10.149.2.24",
        "cvm_ip": "10.149.2.34"
      }
    ],
    "asset_uuid": "aebd05ce-4b88-4f2c-b0f4-af4b43a9a709",
    "asset_name": "poc02",
    "segment_uuid": "64573328-5c18-47b5-bc79-496457c57092",
    "segment_name": "main",
    "physical_check": {
      "00:25:90:d6:05:24": true,
      "00:25:90:d6:05:9e": true,
      "00:25:90:d6:05:26": true,
      "0c:c4:7a:45:e3:c4": true
    },
    "host_check": {
      "10.149.2.21": true,
      "10.149.2.22": true,
      "10.149.2.23": true,
      "10.149.2.24": true
    },
    "prism_check": true,
    "version": "5.10.2",
    "hypervisor": "AHV"
  }''')

sops = SetupOps(cluster)
sops.connect_to_prism()
#sops.setup_networks()
sops.setup_images()