import json
import sys
import logging
import time
import os
import traceback
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
  def check_physically_exist(fvm_ip, fvm_user, fvm_password, ipmi_mac):
    pass

  def check_host_reachable(host_ip):
    pass

  def check_cluster_up(ip, user, name):
    pass

  def get_aos_version(ip, user, name):
    pass

  def get_hypervisor(ip, user, name):
    pass

def test_checkStatusOps():
  CheckStatusOps.check_physically_exist()
  

if __name__ == '__main__':
  test_checkStatusOps()