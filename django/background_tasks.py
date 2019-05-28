import threading
import time
import json
import requests

from task.models import Task
from nutanix_foundation import FoundationOps
from nutanix_cluster import CheckStatusOps

import django.core.management.commands.runserver as runserver
cmd = runserver.Command()
PORT = cmd.default_port

class FoundationTask(threading.Thread):
  def __init__(self, task_uuid, cluster_dict, aos_image, hypervisor_type, hypervisor_image):
    threading.Thread.__init__(self)
    tasks = Task.objects.filter(uuid=task_uuid)
    if len(tasks) > 0:
      self.task = tasks[0]
    else:
      raise Exception('no task uuid')
    self.task_uuid = task_uuid
    self.cluster_dict = cluster_dict
    self.aos_image = aos_image
    self.hypervisor_type = hypervisor_type
    self.hypervisor_image = hypervisor_image

  def run(self):
    try:
      fo = FoundationOps()
      fo.foundation(self.cluster_dict, self.aos_image)
      fo.eula(self.cluster_dict)
      fo.setup(self.cluster_dict)
    except:
      pass

    self.task.is_complete = True

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
      print('StatusCheckTask.run()')
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
      print(response)

    except Exception as e:
      print(e)