import json
import sys
import logging
import time
import os
import traceback
import pings
from nutanix_restapi import NutanixFoundationClient, NutanixRestApiClient

class ClusterStartOps:
  def power_on(ipmi_list):
    for ipmi in ipmi_list:
      user = ipmi['user']
      password = ipmi['password']
      ip = ipmi['ip']

      ipmi_command = 'ipmitool '.format(ip, user, password)
      os.command(ipmi_command)
  

class ClusterStopOps:
  def stop_guest_vms(ip, user, name):
    pass

  def stop_cluster(ip, user, name):
    pass

  def poweroff_cvm(ip, user, name):
    pass

  def poweroff_host(ip, user, name):
    pass


class CheckStatusOps:
  def check_physically_exist(fvm_ip, fvm_user, fvm_password, ipmi_mac_list):
    client = NutanixFoundationClient(fvm_ip, fvm_user, fvm_password)
    results = {}
    for ipmi_mac in ipmi_mac_list:
      result = client.does_mac_exist(ipmi_mac, 'eth0')
      results[ipmi_mac] = result
    return results

  def check_host_reachable(host_ips):
    p = pings.Ping()
    results = {}
    for host_ip in host_ips:
      res = p.ping(host_ip)
      results[host_ip] = res.is_reached()
    return results

  def check_cluster_up(ip, user, password):
    try:
      client = NutanixRestApiClient(ip, user, password)
    except Exception as e:
      return False
    return True

  def get_aos_version(ip, user, password):
    try:
      client = NutanixRestApiClient(ip, user, password)
      (success, version) = client.get_version()
      if not success:
        return ''
      return version
    except Exception as e:
      return ''


  def get_hypervisor(ip, user, password):
    try:
      client = NutanixRestApiClient(ip, user, password)
      (success, version) = client.get_hypervisor()
      if not success:
        return ''
      return version
    except Exception as e:
      return ''

def test_checkStatusOps():
  #results = CheckStatusOps.check_physically_exist('10.149.160.5', 'nutanix', 'nutanix/4u', ['0c:c4:7a:92:95:d4', '0c:c4:7a:66:e1:d3', '0c:c4:7a:66:e2:95', '0c:c4:7a:66:e2:97'])
  #results = CheckStatusOps.check_host_reachable(['10.149.161.21', '10.149.161.22', '10.149.161.23', '10.149.161.24'])
  #results = CheckStatusOps.check_cluster_up('10.149.161.41', 'admin', 'Nutanix/4u!')
  #results = CheckStatusOps.get_aos_version('10.149.161.41', 'admin', 'Nutanix/4u!')
  results = CheckStatusOps.get_hypervisor('10.149.161.41', 'admin', 'Nutanix/4u!')

  print(results)

if __name__ == '__main__':
  test_checkStatusOps()