import threading
import time
import json
import requests
import subprocess
import paramiko
import traceback
import os
import uuid
import sys

from task.models import Task
from nutanix_foundation import FoundationOps, EulaOps, SetupOps
from nutanix_cluster import CheckStatusOps, ClusterStartOps, ClusterStopOps

try:
  last_arg = sys.argv[-1]
  words = last_arg.split(':')
  PORT = int(words[1])
except Exception as e:
  print(e)
  import django.core.management.commands.runserver as runserver
  cmd = runserver.Command()
  PORT = cmd.default_port
print('Running on Port: {}'.format(PORT))

def send_task_update(task_uuid, status, finished=False):
  self_url = 'http://127.0.0.1:{}/api/task_status/{}'.format(PORT, task_uuid)
  d = {
    'status':status,
    'finished':finished
  }
  request_body = json.dumps(d, indent=2)
  response = requests.put(self_url, request_body)


class AnsibleTask(threading.Thread):
  def __init__(self, task_uuid, hosts, user, password, playbook_body):
    threading.Thread.__init__(self)
    self.task_uuid = task_uuid
    self.hosts = hosts
    self.user = user
    self.password = password
    self.playbook_body = playbook_body

    self.step_ssh_copy_id = ''
    self.step_inventory = ''
    self.step_playbook = ''
    self.step_run_playbook = ''

  def ssh_copy_id(self):
    for host in self.hosts:
      host = host.strip()
      if host == '':
        continue
          
      command = 'echo "{}" | sshpass ssh-copy-id  -o StrictHostKeyChecking=no -o ConnectTimeout=3 {}@{}'.format(self.password, self.user, host)
      res_bytes = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
      res_string = res_bytes.decode('utf-8').strip()
      print(res_string)

  def ansible_playbook(self, inventory, playbook):
    command = 'ansible-playbook -i {} {}'.format(inventory, playbook)
    res_bytes = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    return res_bytes.decode('utf-8').strip()

  def make_playbook(self):
    dirpath = './ansible_workspace'
    filename = str(uuid.uuid4())
    filepath = os.path.join(dirpath, filename)
    os.makedirs(dirpath, exist_ok=True)
    with open(filepath, 'w') as f:
      f.write(self.playbook_body)
    return filepath

  def make_inventory(self):
    dirpath = './ansible_workspace'
    filename = str(uuid.uuid4())
    filepath = os.path.join(dirpath, filename)
    os.makedirs(dirpath, exist_ok=True)
    with open(filepath, 'w') as f:
      for host in self.hosts:
        host = host.strip()
        if host == '':
          continue
        line = '{}\n'.format(host)
        f.write(line)
    return filepath

  def status(self):
    text = ''
    text += 'Copy key via ssh-copy-id : {}\n'.format(self.step_ssh_copy_id)
    text += 'Make inventory file      : {}\n'.format(self.step_inventory)
    text += 'Make playbook file       : {}\n'.format(self.step_playbook)
    text += 'Run playbook             : {}\n'.format(self.step_run_playbook)
    return text

  def run(self):
    try:
      self.step_ssh_copy_id = 'Running'
      send_task_update(self.task_uuid, self.status())
      self.ssh_copy_id()

      self.step_ssh_copy_id = 'Done'
      self.step_inventory = 'Running'
      send_task_update(self.task_uuid, self.status())
      inventory_path = self.make_inventory()
      print(inventory_path)

      self.step_inventory = 'Done'
      self.step_playbook = 'Running'
      send_task_update(self.task_uuid, self.status())
      playbook_path = self.make_playbook()
      print(playbook_path)

      self.step_playbook = 'Done'
      self.step_run_playbook = 'Running'
      send_task_update(self.task_uuid, self.status())
      output = self.ansible_playbook(inventory_path, playbook_path)

      self.step_run_playbook = 'Done'
      text = '{}\n\nSuccess.\n\n{}'.format(self.status(), output)
      send_task_update(self.task_uuid, text)

      print(output)
      os.remove(inventory_path)
      os.remove(playbook_path)

    except subprocess.CalledProcessError as exc:
      print(exc.output)
      text = '{}\n\nFailed.\n\n{}'.format(self.status(), exc.output.decode('utf-8').strip())
      send_task_update(self.task_uuid, text, True)
      return

    except Exception as e:
      print(traceback.format_exc())
      text = '{}\n\nFailed.\n\n{}'.format(self.status(), traceback.format_exc())
      send_task_update(self.task_uuid, text, True)
      return

    send_task_update(self.task_uuid, text, True)




class FoundationTask(threading.Thread):
  def __init__(self, task_uuid, cluster_dict, aos_image, hypervisor_type, hypervisor_image):
    threading.Thread.__init__(self)
    self.task_uuid = task_uuid
    self.cluster_dict = cluster_dict
    self.aos_image = aos_image
    self.hypervisor_type = hypervisor_type
    self.hypervisor_image = hypervisor_image

    self.connect_to_fvm = ''
    self.check_ipmi_mac = ''
    self.check_ipmi_ip = ''
    self.check_fvm_isnot_imaging = ''
    self.check_fvm_has_nos_package = ''
    self.set_foundation_settings = ''
    self.configure_ipmi_ip = ''
    self.pre_check = ''
    self.start_foundation = ''
    self.foundation_progress = ''

    self.initial_password = ''
    self.connect_to_prism1 = ''
    self.set_eula_settings = ''

    self.connect_to_prism2 = ''
    self.basics = ''
    self.containers = ''
    self.networks = ''
    self.imaging = ''


  def status(self):
    text = 'Foundation\n'
    text += '  Login to FVM              : {}\n'.format(self.connect_to_fvm)
    text += '  Check IPMI MAC exist      : {}\n'.format(self.check_ipmi_mac)
    text += '  Check IPMI IP conflict    : {}\n'.format(self.check_ipmi_ip)
    text += '  Check FVM is not imaging  : {}\n'.format(self.check_fvm_isnot_imaging)
    text += '  Check FVM has nos image   : {}\n'.format(self.check_fvm_has_nos_package)
    text += '  Apply foundation settings : {}\n'.format(self.set_foundation_settings)
    text += '  Configure IPMI IP         : {}\n'.format(self.configure_ipmi_ip)
    text += '  Pre Check                 : {}\n'.format(self.pre_check)
    text += '  Kick imaging              : {}\n'.format(self.start_foundation)
    text += '  Progress                  : {}\n\n'.format(self.foundation_progress)

    text += 'Eula\n'
    text += '  Set initial password      : {}\n'.format(self.initial_password)
    text += '  Login to Prism            : {}\n'.format(self.connect_to_prism1)
    text += '  Set Eula/Pulse/Alert/Pass : {}\n\n'.format(self.set_eula_settings)

    text += 'Settings\n'
    text += '  Login to Prism            : {}\n'.format(self.connect_to_prism2)
    text += '  Setup Basics              : {}\n'.format(self.basics)
    text += '  Setup Container           : {}\n'.format(self.containers)
    text += '  Setup Network             : {}\n'.format(self.networks)  
    text += '  Kick downloading images   : {}\n'.format(self.imaging) 
    return text

  def run(self):
    try:
      self.foundation()
      self.eula()
      self.setup()

    except Exception as e:
      print(e)
      print(traceback.format_exc())

    self.setup_images = 'Done'
    send_task_update(self.task_uuid, self.status(), True)

  def foundation(self):
    fo = FoundationOps(self.cluster_dict, self.aos_image)

    self.connect_to_fvm = 'Running'
    send_task_update(self.task_uuid, self.status())
    fo.connect_to_fvm()

    self.connect_to_fvm = 'Done'
    self.check_ipmi_mac = 'Running'
    send_task_update(self.task_uuid, self.status())
    fo.check_ipmi_mac()

    self.check_ipmi_mac = 'Done'
    self.check_ipmi_ip = 'Running'
    send_task_update(self.task_uuid, self.status())
    fo.check_ipmi_ip()

    self.check_ipmi_ip = 'Done'
    self.check_fvm_isnot_imaging = 'Running'
    send_task_update(self.task_uuid, self.status())
    fo.check_fvm_isnot_imaging()

    self.check_fvm_isnot_imaging = 'Done'
    self.check_fvm_has_nos_package = 'Running'
    send_task_update(self.task_uuid, self.status())
    fo.check_fvm_has_nos_package()

    self.check_fvm_has_nos_package = 'Done'
    self.set_foundation_settings = 'Running'
    send_task_update(self.task_uuid, self.status())
    fo.set_foundation_settings()

    self.set_foundation_settings = 'Done'
    self.configure_ipmi_ip = 'Running'
    send_task_update(self.task_uuid, self.status())
    fo.configure_ipmi_ip()

    self.configure_ipmi_ip = 'Done'
    self.pre_check = 'Running'
    send_task_update(self.task_uuid, self.status())
    fo.pre_check()

    self.pre_check = 'Done'
    self.start_foundation = 'Running'
    send_task_update(self.task_uuid, self.status())
    fo.start_foundation()

    self.start_foundation = 'Done'
    self.watch_foundation(fo)

  def watch_foundation(self, fo):
    error_counter = 0
    while(True):
      (success, progress) = fo.get_foundation_progress()
      if success:
        self.foundation_progress = '{} %'.format(progress)
        send_task_update(self.task_uuid, self.status())
        if progress == 100:
          time.sleep(3)
          break
        error_counter = 0
        time.sleep(15)

      else:
        error_counter += 1
        if error_counter >= 5:
          print('  Failed to getting progress 5 times sequentially. Abort.')
          raise ErrorException('Failed to getting progress 5 times sequentially.')
        time.sleep(3)

  def eula(self):
    eo = EulaOps(self.cluster_dict)

    self.initial_password = 'Running'
    send_task_update(self.task_uuid, self.status())
    eo.set_initial_password()

    self.initial_password = 'Done'
    self.connect_to_prism1 = 'Running'
    send_task_update(self.task_uuid, self.status())
    eo.connect_to_prism()

    self.connect_to_prism1 = 'Done'
    self.set_eula_settings = 'Running'
    send_task_update(self.task_uuid, self.status())
    eo.set_initial_settings()

    self.set_eula_settings = 'Done'
    send_task_update(self.task_uuid, self.status())


  def setup(self):
    so = SetupOps(self.cluster_dict)

    self.connect_to_prism2 = 'Running'
    send_task_update(self.task_uuid, self.status())
    so.connect_to_prism()

    self.connect_to_prism2 = 'Done'
    self.basics = 'Running'
    send_task_update(self.task_uuid, self.status())
    so.setup_basics()

    self.basics = 'Done'
    self.containers = 'Running'
    send_task_update(self.task_uuid, self.status())
    so.setup_containers()

    self.containers = 'Done'
    self.networks = 'Running'
    send_task_update(self.task_uuid, self.status())
    so.setup_networks()

    self.networks = 'Done'
    self.imaging = 'Running'
    send_task_update(self.task_uuid, self.status())
    so.setup_images()

    self.imaging = 'Done'
    send_task_update(self.task_uuid, self.status(), True)


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