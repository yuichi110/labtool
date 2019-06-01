import threading
import time
import json
import requests
import subprocess
import paramiko

from task.models import Task
from nutanix_foundation import FoundationOps
from nutanix_cluster import CheckStatusOps, ClusterStartOps, ClusterStopOps

import django.core.management.commands.runserver as runserver
cmd = runserver.Command()
PORT = cmd.default_port

def send_task_update(task_uuid, status, finished=False):
  self_url = 'http://127.0.0.1:{}/api/task_status/{}'.format(PORT, task_uuid)
  d = {
    'status':status,
    'finished':finished
  }
  request_body = json.dumps(d, indent=2)
  response = requests.put(self_url, request_body)


class FoundationTask(threading.Thread):
  def __init__(self, task_uuid, cluster_dict, aos_image, hypervisor_type, hypervisor_image):
    threading.Thread.__init__(self)
    self.task = Task.objects.get(uuid=task_uuid)
    self.task_uuid = task_uuid
    self.cluster_dict = cluster_dict
    self.aos_image = aos_image
    self.hypervisor_type = hypervisor_type
    self.hypervisor_image = hypervisor_image

  def status(self):
    return ''

  def run(self):
    try:
      fo = FoundationOps(self.cluster_dict, self.aos_image)
      fo.connect_to_fvm()
      fo.check_ipmi_mac_ip()
      fo.check_fvm_isnot_imaging()
      fo.check_fvm_has_nos_package()
      fo.set_foundation_settings()
      fo.configure_ipmi_ip()
      fo.pre_check()
      fo.start_foundation()

      while(True):
        fo.get_foundation_progress()
        break

      eo = EuraOps()

    except:
      pass

    self.task.is_complete = True


class ClusterStartTask(threading.Thread):
  def __init__(self, task_uuid, ipmi_ips, host_ips, cvm_ips, prism_ip, prism_user, prism_password):
    threading.Thread.__init__(self)
    self.task_uuid = task_uuid
    self.ipmi_ips = ipmi_ips
    self.host_ips = host_ips
    self.cvm_ips = cvm_ips
    self.prism_ip = prism_ip
    self.prism_user = prism_user
    self.prism_password = prism_password

    self.power_on = ''
    self.waiting_host_up = ''
    self.waiting_cvm_up = ''
    self.starting_cluster = ''

  def status(self):
    text = ''
    text += 'Power on hosts : {}\n'.format(self.power_on)
    text += 'Waiting hosts  : {}\n'.format(self.waiting_host_up)
    text += 'Waiting CVMs   : {}\n'.format(self.waiting_cvm_up)
    text += 'Cluster Start  : {}\n'.format(self.starting_cluster)
    return text

  def run(self):
    try:
      ops = ClusterStartOps(self.ipmi_ips, self.host_ips, self.cvm_ips, self.prism_ip, self.prism_user, self.prism_password)

      self.power_on = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.power_on_all_servers()

      self.power_on = 'Done'
      self.waiting_host_up = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.check_all_hosts_are_accessible()

      self.waiting_host_up = 'Done'
      self.waiting_cvm_up = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.power_on_all_cvms()

      self.waiting_cvm_up = 'Done'
      self.starting_cluster = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.start_cluster()

    except:
      pass

    self.starting_cluster = 'Done'
    send_task_update(self.task_uuid, self.status(), True)


class ClusterStopTask(threading.Thread):
  def __init__(self, task_uuid, prism_ip, prism_user, prism_password):
    threading.Thread.__init__(self)
    self.task_uuid = task_uuid    
    self.prism_ip = prism_ip
    self.prism_user = prism_user
    self.prism_password = prism_password

    self.calm = ''
    self.guest = ''
    self.files = ''
    self.pc = ''
    self.allvm = ''
    self.cluster = ''
    self.cvm = ''
    self.host = ''

  def status(self):
    text = ''
    text += 'Stopping Calm          : {}\n'.format(self.calm)
    text += 'Stopping Normal VMs    : {}\n'.format(self.guest)
    text += 'Stopping Files         : {}\n'.format(self.files)
    text += 'Stopping Prism Central : {}\n'.format(self.pc)
    text += 'Stopping All VMs       : {}\n'.format(self.allvm)
    text += 'Stopping Cluster       : {}\n'.format(self.cluster)
    text += 'Stopping CVM           : {}\n'.format(self.cvm)
    text += 'Stopping Host          : {}\n'.format(self.host)    
    return text

  def run(self):
    try:
      ops = ClusterStopOps(self.prism_ip, self.prism_user, self.prism_password)

      self.calm = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.stop_calm()

      self.calm = 'Done'
      self.guest = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.stop_non_agent_guests()

      self.guest = 'Done'
      self.files = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.stop_files()

      self.files = 'Done'
      self.pc = 'Running'
      send_task_update(self.task_uuid, self.status())      
      ops.stop_pc()

      self.pc = 'Done'
      self.allvm = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.stop_all_vms()

      self.allvm = 'Done'
      self.cluster = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.stop_cluster()

      self.cluster = 'Done'
      self.cvm = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.stop_cvms()

      self.cvm = 'Done'
      self.host = 'Running'
      send_task_update(self.task_uuid, self.status())
      ops.stop_hosts()

    except:
      pass

    self.host = 'Done'
    send_task_update(self.task_uuid, self.status(), True)


class StatusCheckTask(threading.Thread):
  def __init__(self, cluster_uuid, fvm_ip, fvm_user, fvm_password, ipmi_mac_list, host_ips, prism_ip, prism_user, prism_password, sleep):
    threading.Thread.__init__(self)
    self.cluster_uuid = cluster_uuid
    self.fvm_ip = fvm_ip
    self.fvm_user = fvm_user
    self.fvm_password = fvm_password
    self.ipmi_mac_list = ipmi_mac_list
    self.host_ips = host_ips
    self.prism_ip = prism_ip
    self.prism_user = prism_user
    self.prism_password = prism_password
    self.sleep = sleep

  def run(self):
    try:
      #print('StatusCheckTask.run()')
      time.sleep(self.sleep)

      mac_results = CheckStatusOps.check_physically_exist(self.fvm_ip, self.fvm_user, self.fvm_password, self.ipmi_mac_list)
      host_results = CheckStatusOps.check_host_reachable(self.host_ips)
      prism_results = CheckStatusOps.check_cluster_up(self.prism_ip, self.prism_user, self.prism_password)
      version_results = CheckStatusOps.get_aos_version(self.prism_ip, self.prism_user, self.prism_password)
      hypervisor_results = CheckStatusOps.get_hypervisor(self.prism_ip, self.prism_user, self.prism_password)

      d = {
        'physical_check':mac_results,
        'host_check':host_results,
        'prism_check':prism_results,
        'version':version_results,
        'hypervisor':hypervisor_results
      }

      self_url = 'http://127.0.0.1:{}/api/cluster_status/{}'.format(PORT, self.cluster_uuid)
      request_body = json.dumps(d, indent=2)
      response = requests.put(self_url, request_body)
      #print(response)

    except Exception as e:
      print(e)