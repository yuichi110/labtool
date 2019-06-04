import json
import sys
import logging
import time
import os
import traceback
import subprocess
import paramiko
from nutanix_restapi import NutanixFoundationClient, NutanixRestApiClient

###
### Cluster Start
###

class ClusterStartOps:

  def __init__(self, ipmi_ips, host_ips, cvm_ips, prism_ip, prism_user, prism_password):
    self.ipmi_ips = ipmi_ips
    self.host_ips = host_ips
    self.cvm_ips = cvm_ips
    self.prism_ip = prism_ip
    self.prism_user = prism_user
    self.prism_password = prism_password

  def power_on_all_servers(self):
    print('power_on_all_servers()')

    def is_server_power_on(ip, user, password):
      try:
        command = 'ipmitool -I lanplus -U {} -P {} -H {} power status'.format(user, password, ip)
        res_bytes = subprocess.check_output(command.split())
        res_string = res_bytes.decode('utf-8').strip()
      except Exception as e:
        print(e)
        return False

      words = res_string.lower().split()
      if 'off' in words:
        return False
      if 'on' in words:
        return True
      return False

    def is_all_server_power_on(ipmi_ips):
      all_up = True
      for ipmi_ip in ipmi_ips:
        power_on = is_server_power_on(ipmi_ip, 'ADMIN', 'ADMIN')
        if not power_on:
          all_up = False
          break
      return all_up

    def power_on_server(ip, user, password):
      try:
        command = 'ipmitool -I lanplus -U {} -P {} -H {} chassis power on'.format(user, password, ip)
        res = subprocess.check_output(command.split()).decode('utf-8').strip()
      except Exception as e:
        print(e)

    # if not all servers are up, try power on. And check again few times.
    for i in range(5):
      if is_all_server_power_on(self.ipmi_ips):
        return
      for ipmi_ip in self.ipmi_ips:
        print('power on server on ipmi: {}'.format(ipmi_ip))
        power_on_server(ipmi_ip, 'ADMIN', 'ADMIN')
      time.sleep(20)

    raise Exception("Unable to power on servers via IPMI.")

  def check_all_hosts_are_accessible(self):
    print('check_all_hosts_are_accessible()')

    def is_host_accessible(host_ip, user, password):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host_ip, username=user, password=password, timeout=3.0)
        command = 'date'
        client.exec_command(command)
      except Exception as e:
        print(e)
        return False
      return True

    def is_all_host_accessible(host_ips, user, password):
      all_up = True
      for host_ip in host_ips:
        power_on = is_host_accessible(host_ip, user, password)
        if not power_on:
          all_up = False
          break
      return all_up

    # Check all hosts are up
    ok = False
    for i in range(10):
      if is_all_host_accessible(self.host_ips, 'root', 'nutanix/4u'):
        ok = True
        break
      print('Waiting all hosts are up and accessible via ssh.')
      time.sleep(60)
    if not ok:
      raise Exception('Unable to access few hosts')

  
  def power_on_all_cvms(self):
    print('power_on_all_cvms()')

    def is_host_accessible(host_ip, user, password):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host_ip, username=user, password=password, timeout=3.0)
        command = 'date'
        client.exec_command(command)
      except Exception as e:
        print(e)
        return False
      return True

    def is_all_host_accessible(host_ips, user, password):
      all_up = True
      for host_ip in host_ips:
        power_on = is_host_accessible(host_ip, user, password)
        if not power_on:
          all_up = False
          break
      return all_up

    # Check all CVMs are up
    ok = False
    for i in range(5):
      if is_all_host_accessible(self.cvm_ips, 'nutanix', 'nutanix/4u'):
        ok = True
        break
      print('Waiting all CVMs are up and accessible via ssh.')
      time.sleep(30)
    if not ok:
      raise Exception('Unable to access few cvms')


  def start_cluster(self):
    print('start_cluster()')

    def issue_cluster_start(cvm_ip, user, password):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(cvm_ip, username=user, password=password, timeout=3.0)
        command = '/usr/local/nutanix/cluster/bin/cluster start'
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode().strip())
        print(stderr.read().decode().strip())
      except Exception as e:
        print(e)

    # Try login to Prism. If fails, issue "cluster start" on first CVM
    for i in range(5):
      try:
        NutanixRestApiClient(self.prism_ip, self.prism_user, self.prism_password)
        return
      except:
        issue_cluster_start(self.cvm_ips[0], 'nutanix', 'nutanix/4u')
      time.sleep(30)


class ClusterStopOps:
  
  def __init__(self, prism_ip, prism_user, prism_password):
    self.prism_ip = prism_ip
    self.prism_user = prism_user
    self.prism_password = prism_password
    
    self.session = NutanixRestApiClient(prism_ip, prism_user, prism_password)
    (success, result) = self.session.get_ipmi_host_cvm_ips()
    if not success:
      raise Exception("Failed to get IPs")
    (self.ipmi_list, self.host_list, self.cvm_list) = result


  def stop_calm(self):
    print('stop_calm()')
    pass

  def stop_non_agent_guests(self):
    print('stop_non_agent_guests()')

    def get_poweredon_guest_vms():
      (_, pc_vms) = self.session.get_pc_vms()
      (_, fsvms) = self.session.get_fsvms()
      (_, agentvms) = self.session.get_agent_vms()
      special_vms = pc_vms + fsvms + agentvms
      (_, poweredon_vms) = self.session.get_poweredon_vms()

      poweredon_guestvms = []
      for vm in poweredon_vms:
        if vm not in special_vms:
          poweredon_guestvms.append(vm)
      return poweredon_guestvms

    def stop_vms(vm_list, force=False):
      if len(vm_list) == 0:
        return

      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.prism_ip, username=self.prism_user, password=self.prism_password)

        if force:
          command = 'acli vm.off {}'.format(','.join(poweredon_guest_vms))
        else:
          command = 'acli vm.shutdown {}'.format(','.join(poweredon_guest_vms))
        stdin, stdout, stderr = client.exec_command(command)
      except Exception as e:
        print(e)

    # Stop normal guest vms.
    for i in range(5):
      poweredon_guest_vms = get_poweredon_guest_vms()
      if len(poweredon_guest_vms) == 0:
        break

      if i > 3:
        stop_vms(poweredon_guest_vms, True)
      else:
        stop_vms(poweredon_guest_vms)
      time.sleep(10)


  def stop_files(self):
    print('stop_files()')

    def issue_stop_command():
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.prism_ip, username=self.prism_user, password=self.prism_password)

        command = '/usr/local/nutanix/minerva/bin/afs infra.stop'
        stdin, stdout, stderr = client.exec_command(command)
      except Exception as e:
        print(e)

    def is_all_fsvm_down(fsvms):
      for fsvm in fsvms:
        (_, power) = self.session.get_vm_powerstate(fsvm)
        logger.debug('FSVM {} : Power {}'.format(fsvm, power))
        if power == 'on':
          return False
      return True

    issue_stop_command()
    (_, fsvms) = self.session.get_fsvms()
    for i in range(20):
      if is_all_fsvm_down(fsvms):
        return
      time.sleep(10)


  def stop_pc(self):
    print('stop_pc()')

    def pc_cluster_stop(pc_ip):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(pc_ip, username='nutanix', password='nutanix/4u')
        command = "/home/nutanix/prism/cli/ncli cluster stop"
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode().strip())
      except Exception as e:
        print(e)

    def is_pc_cluster_stop(pc_ip):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(pc_ip, username='nutanix', password='nutanix/4u')
        command = "/usr/local/nutanix/cluster/bin/cluster status | grep state"
        stdin, stdout, stderr = client.exec_command(command)
        buf = stdout.read().decode().strip()
        cluster_state = buf.split()
        return cluster_state[-1] == "stop"
      except Exception as e:
        print(e)
      return False

    def pc_vm_stop(pc_ip):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(pc_ip, username='nutanix', password='nutanix/4u')

        command = "sudo /usr/sbin/shutdown -h now"
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode().strip())
      except Exception as e:
        print(e)

    def is_pc_vm_down(pc_vm):
        try:
          (_, power) = self.session.get_vm_powerstate(pc_vm)
          logger.debug('PCVM {} : Power {}'.format(pc_vm, power))
          if power == 'on':
            return False
        except Exception as e:
          print(e)
          return False


    # Get PC VMs
    (_, pc_vms) = self.session.get_pc_vms()
    
    # Exit if no pcs are up
    if (len(pc_vms)) == 0:
      return
    all_down = True
    for pc_vm in pc_vms:
      if not is_pc_vm_down(pc_vm):
        all_down = False
        break
    if all_down:
      return

    # Cluster stop on all PCs 
    for pc_vm in pc_vms:
      (_, pc_ip) = self.session.get_vm_ip(pc_vm)
      if not is_pc_cluster_stop(pc_ip):
        pc_cluster_stop(pc_ip)
        for i in range(5):
          if is_pc_cluster_stop(pc_ip):
            return
          time.sleep(10)

    # Power Off on all PCs
    for pc_vm in pc_vms:
      if not is_pc_vm_down(pc_vm):
        (_, pc_ip) = self.session.get_vm_ip(pc_vm)
        pc_vm_stop(pc_ip)
        for i in range(10):
          if is_pc_vm_down(pc_vm):
            break
          time.sleep(5)



  def stop_all_vms(self):
    print('stop_all_vms()')

    def stop_vms(vm_list, force=False):
      if len(vm_list) == 0:
        return

      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.prism_ip, username=self.prism_user, password=self.prism_password)

        if force:
          command = 'acli vm.off {}'.format(','.join(poweredon_guest_vms))
        else:
          command = 'acli vm.shutdown {}'.format(','.join(poweredon_guest_vms))
        stdin, stdout, stderr = client.exec_command(command)
      except Exception as e:
        print(e)

    # Stop all VMs
    for i in range(5):
      (_, poweredon_vms) = self.session.get_poweredon_vms()

      if i > 3:
        stop_vms(poweredon_vms, True)
      else:
        stop_vms(poweredon_vms)
      time.sleep(10)


  def stop_cluster(self):
    print('stop_cluster()')

    def cluster_stop(cvm_ip):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(cvm_ip, username='nutanix', password='nutanix/4u')
        command = "/home/nutanix/prism/cli/ncli cluster stop"
        stdin, stdout, stderr = client.exec_command(command)
        print(stdout.read().decode().strip())
      except Exception as e:
        print(e)

    def is_cluster_stop(cvm_ip):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(cvm_ip, username='nutanix', password='nutanix/4u')
        command = "/usr/local/nutanix/cluster/bin/cluster status | grep state"
        stdin, stdout, stderr = client.exec_command(command)
        buf = stdout.read().decode().strip()
        cluster_state = buf.split()
        return cluster_state[-1] == "stop"
      except Exception as e:
        print(e)
      return False

    cluster_stop(self.cvm_list[0])
    for i in range(10):
      is_cluster_stop(self.cvm_list[0])
      time.sleep(5)


  def stop_cvms(self):
    print('stop_cvms()')

    def cvm_stop(cvm_ip):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(cvm_ip, username='nutanix', password='nutanix/4u')

        command = "sudo /usr/sbin/shutdown -h now"
        stdin, stdout, stderr = client.exec_command(command)
      except Exception as e:
        print(e)

    def is_cvm_stop(host_ip):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host_ip, username='root', password='nutanix/4u')

        command = "bash -c 'virsh list | wc -l'"
        stdin, stdout, stderr = client.exec_command(command)
        buf = stdout.read().decode().strip()
        return buf == '3'
      except Exception as e:
        print(e)
      return False

    for cvm_ip in self.cvm_list:
      cvm_stop(cvm_ip)

    for i in range(10):
      all_down = True
      for host_ip in self.host_list:
        if not is_cvm_stop(host_ip):
          all_down = False
      if all_down:
        return
      time.sleep(5)


  def stop_hosts(self):
    print('stop_hosts()')

    def stop_host(host_ip):
      try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host_ip, username='root', password='nutanix/4u')

        command = "shutdown -h now"
        stdin, stdout, stderr = client.exec_command(command)
      except Exception as e:
        print(e)

    for host_ip in self.host_list:
      stop_host(host_ip)



class CheckStatusOps:
  def check_physically_exist(fvm_ip, fvm_user, fvm_password, ipmi_mac_list):
    client = NutanixFoundationClient(fvm_ip, fvm_user, fvm_password)
    results = {}
    for ipmi_mac in ipmi_mac_list:
      result = client.does_mac_exist(ipmi_mac, 'eth0')
      results[ipmi_mac] = result
    return results

  def check_host_reachable(host_ips):
    results = {}
    for host_ip in host_ips:
      try:
        command = 'ping {} -c 2 -W 2'.format(host_ip)
        subprocess.check_output(command, shell=True)
        results[host_ip] = True
      except:
        results[host_ip] = False
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

def test_ClusterStartOps():
  ops = ClusterStartOps(['10.149.161.11', '10.149.161.12', '10.149.161.13', '10.149.161.14'], 
    ['10.149.161.21', '10.149.161.22', '10.149.161.23', '10.149.161.24'], 
    ['10.149.161.31', '10.149.161.32', '10.149.161.33', '10.149.161.34'],
    '10.149.161.41', 'admin', 'Nutanix/4u!123')
  ops.power_on_all_servers()
  ops.check_all_hosts_are_accessible()
  ops.power_on_all_cvms()
  ops.start_cluster()

def test_ClusterStopOps():
  ops = ClusterStopOps('10.149.161.41', 'admin', 'Nutanix/4u!123')
  ops.stop_calm()
  ops.stop_files()
  ops.stop_non_agent_guests()
  ops.stop_pc()
  ops.stop_all_vms()
  ops.stop_cluster()
  ops.stop_cvms()
  ops.stop_hosts()


if __name__ == '__main__':
  #test_ClusterStartOps()
  test_ClusterStopOps()