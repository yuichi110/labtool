import json
import sys
import logging
import time
import os
import traceback
from nutanix_restapi import NutanixFoundationClient, NutanixRestApiClient

INITIAL_PASSWORD = 'nutanix/4u'
TEMPORARY_PASSWORD = 'SREs4eva!'
CONFIG_FILE = 'foundation_config.json'

###
### Parse command and get info from config file.
###

class FoundationOps:

  def __init__(self, cluster, nos_version):
    self.cluster = cluster
    self.nos_version = nos_version

  def connect_to_fvm(self):
    print('Foundation-01 : Connecting to Foundation VM.')
    logger = NutanixRestApiClient.create_logger('foundation_rest.log', logging.DEBUG)
    foundation_vm = self.cluster['foundation_vms']
    fvm_ip = foundation_vm['ip_addresses'][0]
    fvm_user = foundation_vm['user']
    fvm_password = foundation_vm['password']
    print('  ip : {}'.format(fvm_ip))
    print('  user : {}'.format(fvm_user))
    print('  password : {}'.format(fvm_password))
    self.client = NutanixFoundationClient(fvm_ip, fvm_user, fvm_password, logger)

  def check_ipmi_mac_ip(self):   
    print('Foundation-02 : Check IPMI MAC and IPMI address are OK.')
    problems = []
    for node in self.cluster['nodes']:
      position = node['position'].upper()
      print('  Checking Node_{}'.format(position))

      # MAC address check
      ipmi_mac = node['ipmi_mac']
      result = self.client.does_mac_exist(ipmi_mac, 'eth0')
      if not result:
        text = '    Failed. IPMI MAC address "{}" does not exist on the segment. Abort after all check finished.\n'.format(ipmi_mac)
        problems.append("Node-{}: IPMI MAC({}) doesn't exist on the segment".format(position, ipmi_mac))
      else:
        text = '    Success. IPMI MAC address "{}" exists on the segment.\n'.format(ipmi_mac)
      
      # IP address check
      ipmi_ip = node['ipmi_ip']
      result = self.client.get_mac_from_ip(ipmi_ip)
      if result == '':
        text += '    Success. IPMI IP address "{}" does not exist.'.format(ipmi_ip)
      elif result == ipmi_mac:
        text += '    Success. IPMI already has IP address "{}".'.format(ipmi_ip)
      else:
        # someone uses same ip. abort.
        text += '    Failed. IPMI IP address "{}" is already used by another MAC Address "{}". Abort after all check finished.'.format(ipmi_ip, result)
        problems.append("Node-{}: IPMI IP({}) is already used by another machine".format(position, ipmi_ip))
      print(text)

    if len(problems) != 0:
      raise ErrorException('\n'.join(problems))

    print('  Success for all checks.')

  def check_fvm_isnot_imaging(self):
    print('Foundation-03 : Check currently imaging or not.')
    (success, result) = client.get_progress()
    if not success:
      print('  Failed with error "{}"'.format(response['error']))
      raise ErrorException('Failed to get Foundation VM progress.')

    if result['imaging_stopped']:
      print('  Success. Foundation VM is not imaging now.')
    else:
      print('  Failed. Foundation VM is imaging now. If it is not intended, please abort manually on the Foundation VM.')
      raise ErrorException('Foundation VM is imaging now. Please wait or abort manually.')

  def check_fvm_has_nos_package(self):
    print('Foundation-04 : Check whether foundation vm has nos_package or not.')
    (success, nos_packages) = client.get_nos_packages()
    if not success:
      print('  Failed with error "{}"'.format(response['error']))
      raise ErrorException('Failed to get AOS package list.')

    if nos_package in nos_packages:
      print('  Foundation VM has nos_package "{}"'.format(nos_package))
    else:
      print('  Foundation VM does not have nos_package "{}". But having "{}". Abort.'.format(nos_package, nos_packages))
      raise ErrorException("Foundation VM doesn't have nos_package '{}'".format(nos_package))

  def set_foundation_setting(self):
    print('Foundation-05 : Reset Foundation VM')
    (success, result) = client.reset_state()
    if success:
      print('  Success')
    else:
      print('  Failed with error "{}"'.format(response['error']))
      raise ErrorException("Failed to reset foundation state.")

    print('Foundation-06 : Choose primary nic to "eth0"')
    (success, nics) = client.get_nics()
    if not success:
      print('  Failed. Unable to get nic list.')
      raise ErrorException("Failed to get nic list")
    primary_nic = ''
    for (nic, nic_info) in nics.items():
      if nic_info['name'].lower() == 'eth0':
        primary_nic = nic
        break
    if primary_nic == '':
      print('  Failed. Unable to find "eth0".')
      raise ErrorException('Failed to find nic "eth0" on nic list')
    (success, result) = client.choose_primary_nic(primary_nic)
    if success:
      print('  Success')
    else:
      print('  Failed with error "{}"'.format(response['error']))
      raise ErrorException('Failed to choose "eth0" as primary nic.')

  def configure_ipmi_ip(self):
    print('Foundation-07 : Configure IPMI IP. May take few minutes.')
    (success, result) = client.ipmi_config(netmask, gateway, nodeinfo_list,
      cluster_name, external_ip, name_server, ntp_server, nos_package)
    if success:
      print('  Success')
    else:
      print('  Failed with error "{}"'.format(response['error']))
      raise ErrorException('Failed to configure IPMI IP.')

  def pre_check(self):
    print('Foundation-08 : Pre Check. May take few minutes.')
    (success, result) = client.pre_check(netmask, gateway, nodeinfo_list,
      cluster_name, external_ip, name_server, ntp_server, nos_package)
    if success:
      print('  Success')
    else:
      print('  Failed with error "{}"'.format(response['error']))
      raise ErrorException('Failed to do pre check.')

  def start_foundation(self):
    print('Foundation-09 : Kicking imaging nodes.')
    (success, result) = client.image_nodes(netmask, gateway, nodeinfo_list,
      cluster_name, external_ip, name_server, ntp_server, nos_package)
    if success:
      print('  Success')
    else:
      print('  Failed with error "{}"'.format(response['error']))
      raise ErrorException('Failed to kick imaging nodes.')

  def get_foundation_progress(self):
    (success, result) = client.get_progress()
    if success:
      for node in result['nodes']:
        node_ip = node['hypervisor_ip']
        node_percent = node['percent_complete']
        node_status = node['status']
        print('node({}) {}% : {}'.format(node_ip, node_percent, node_status))

      cluster_name = result['clusters'][0]['cluster_name']
      cluster_percent = result['clusters'][0]['percent_complete']
      cluster_status = result['clusters'][0]['status']
      print('cluster({}) {}% : {}'.format(cluster_name, cluster_percent, cluster_status))
      aggregate_percent = result['aggregate_percent_complete']
      print('aggregate {}%'.format(aggregate_percent))

      if aggregate_percent == 100:
        time.sleep(3)
        break
      else:
        if result['abort_session'] == True:
          print('  Failed. Imaging was aborted.')
          exit(-1)
        elif result['imaging_stopped'] == True:
          print('  Failed. Imaging was stopped.')
          raise ErrorException('Failed. Imaging was stopped.')

      print('=== waiting 15 secs ===')
      time.sleep(15)
      error_counter = 0

    else:
      # failed to get status
      print('  Failed to getting progress. Try again soon.')
      time.sleep(3)
      error_counter += 1
      if error_counter >= 5:
        print('  Failed to getting progress 5 times sequentially. Abort.')
        raise ErrorException('Failed to getting progress 5 times sequentially.')


  def _get_nodeinfo_list(self, cluster):
    nodeinfo_list = []
    for node in cluster['nodes']:
      nodeinfo = (node['ipmi_mac'], node['ipmi_ip'], node['host_ip'],
        node['cvm_ip'], node['host_name'], node['position'])
      nodeinfo_list.append(nodeinfo)
    return nodeinfo_list

  ###
  ### Foundation
  ###

  '''
  def foundation(self, cluster, nos_package):

    netmask = cluster['netmask']
    gateway = cluster['gateway']
    nodeinfo_list = self.get_nodeinfo_list(cluster)
    cluster_name = cluster['name']
    external_ip = cluster['external_ip']
    name_server = cluster['name_server']
    ntp_server = cluster['ntp_server']

    print('Foundation Start!!')

    logger = NutanixRestApiClient.create_logger('foundation_rest.log', logging.DEBUG)
    try:
      foundation_vm = cluster['foundation_vms']
      fvm_ip = foundation_vm['ip_addresses'][0]
      fvm_user = foundation_vm['user']
      fvm_password = foundation_vm['password']
      print('  ip : {}'.format(fvm_ip))
      print('  user : {}'.format(fvm_user))
      print('  password : {}'.format(fvm_password))
      client = NutanixFoundationClient(fvm_ip, fvm_user, fvm_password, logger)
      (success, fvm_version) = client.get_version()
      if not success:
        raise Exception()
      print('  Success. Foundation VM version "{}"'.format(fvm_version))
    except:
      print('  Failed with error "Unable to make session."'.format(fvm_ip, fvm_user, fvm_password))
      raise ErrorException('Failed to make session to foundation vm "{}"'.format(fvm_ip))


    self.check_ipmi_mac_ip(client, cluster)
    '''









class EulaOps:

  def __init__(self, cluster):
    self.cluster = cluster

  def set_initial_password():
    print('Eula Start!!')
    print('Eula-1 : Initialize Prism password to temporary one "{}"'.format(TEMPORARY_PASSWORD))
    (success, result) = NutanixRestApiClient.change_default_system_password(prism_ip, INITIAL_PASSWORD, TEMPORARY_PASSWORD)
    if success:
      print('  Success')
    else:
      print('  Failed with error "{}"'.format(result['error']))
      raise ErrorException('Failed to initialize Prism password. "{}"'.format(result['error']))

  def connect_to_prism(self):
    print('Eula-2 : Make session to Prism')
    logger = NutanixRestApiClient.create_logger('setup_cluster_rest.log', logging.DEBUG)
    try:
      self.session = NutanixRestApiClient(prism_ip, prism_user, TEMPORARY_PASSWORD, logger)
      print('  Success')
    except:
      print('  Failed with error "Connection or Credential problem"')
      raise ErrorException('Failed to make connection to Prism.')

  def set_initial_settings(self):
    print('Eula-3 : Set Eula (User:Yuichi, Company:Nutanix, Position:Inside SE)')
    (success, result) = session.set_eula('Yuichi', 'Nutanix', 'Inside SE')
    if success:
      print('  Success')
    else:
      print('  Failed with error "{}"'.format(response['error']))
      raise ErrorException('Failed to set Eula.')

    print('Eula-4 : Set initial pulse settings.')
    (success, result) = session.set_initial_pulse()
    if success:
      print('  Success')
    else:
      print('  Failed with error "{}"'.format(response['error']))
      raise ErrorException('Failed to set initial pulse setting.')

    print('Eula-5 : Set initial alert settings.')
    (success, result) = session.set_initial_alerts()
    if success:
      print('  Success')
    else:
      print('  Failed with error "{}"'.format(response['error']))
      raise ErrorException('Failed to set alert settings.')

    print('Eula-6 : Change password to "{}"'.format(password))
    if password == TEMPORARY_PASSWORD:
      print('  Same password. Skip.')
    else:
      (success, result) = session.change_password(TEMPORARY_PASSWORD, password)
      if success:
        print('  Success')
      else:
        print('  Failed with error "{}"'.format(response['error']))
        raise ErrorException('Failed to change password.')


  '''
  def eula(self, cluster):
    prism_ip = cluster['external_ip']
    prism_user = cluster['prism_user']
    password = cluster['prism_password']

    print('Eula Finished!!')
  '''

  ###
  ### SETUP
  ###


class SetupOps:
  def __init__(self, cluster):
    self.cluster = cluster

    prism_ip = cluster['external_ip']
    prism_user = cluster['prism_user']
    prism_password = cluster['prism_password']
    print('Setup-1 : Make session to Prism.')
    logger = NutanixRestApiClient.create_logger('setup_cluster_rest.log', logging.DEBUG)
    print('  ip : {}'.format(prism_ip))
    print('  user : {}'.format(prism_user))
    print('  password : {}'.format(prism_password))
    self.session = NutanixRestApiClient(prism_ip, prism_user, prism_password, logger)
    print('  Success')


  def setup_basics(self):
    basics = cluster['basics']
    language = basics['language']

    print('  Change language to "{}"'.format(language))
    language = language.lower()
    lmap = {'en-us':'en-US', 'ja-jp':'ja-JP', 'zh-cn':'zh-CN'}
    if language not in ['en-us', 'ja-jp', 'zh-cn']:
      print('    Failed. supports only {}'.format(['en-US', 'ja-JP', 'zh-CN']))
      raise ErrorException('Failed. Unsupported language "{}".'.format(lmap[language]))

    (success, result) = session.change_language(lmap[language])
    if success:
      print('    Success')
    else:
      print('    Failed with error "{}"'.format(response['error']))
      raise ErrorException('Failed to change language.')


  def setup_container(self):
    containers = cluster['containers']

    # get existing containers
    (success, existing_containers) = session.get_container_names()
    if not success:
      raise Exception('Error happens on getting existing container names.')
    print('  Existing containers "{}"'.format(existing_containers))

    # delete useless containers
    for existing_container in existing_containers:
      if existing_container in containers:
        continue
      (success, container_info) = session.get_container_info(existing_container)
      if not success:
        raise Exception('Error happens on getting container info "{}".'.format(existing_container))
      if container_info['usage'] != '0':
        continue
      print('  Deleting useless container "{}"'.format(existing_container))
      (success, _) = session.delete_container(existing_container)
      if not success:
        raise Exception('Error happens on deleting container "{}".'.format(existing_container))  

    # create containers which doesn't exist.
    task_list = []
    for container in containers:
      if container in existing_containers:
        continue
      print('  Creating container "{}"'.format(container))
      (success, taskuuid) = session.create_container(container)
      if not success:
        raise Exception('Error happens on creating container "{}".'.format(container))
      task_list.append(taskuuid)

    # wait till end
    wait_tasks(session, task_list)

  def setup_network(self):
    networks = []
    for (name, config_network) in cluster['networks'].items():
      if not config_network['use_dhcp']:
        networks.append((name, config_network['vlan']))
        continue
      network = config_network['network']
      prefix = config_network['prefix']
      gateway = config_network['gateway']
      dns = config_network['dns']
      pools = []
      for config_pool in config_network['pools']:
        config_from = config_pool['from']
        if 'POCID' in config_from:
          config_from = config_from.replace('POCID', cluster['POCID'])
        config_to = config_pool['to']
        if 'POCID' in config_to:
          config_to = config_to.replace('POCID', cluster['POCID'])      
        pools.append((config_from, config_to))
      networks.append((network, prefix, gateway, dns, pools))

    (success, existing_networks) = session.get_network_names()
    if not success:
      raise Exception('Error happens on getting existing networks.')
    print('  Existing networks "{}"'.format(existing_networks))

    network_names = []
    for network in networks:
      network_names.append(network[0])

    # delete useless network
    for existing_network in existing_networks:
      if existing_network in network_names:
        continue
      (success, used) = session.is_network_used(existing_network)
      if not success:
        raise Exception('Error happens on getting existing networks.')
      if used:
        continue

      print('  Deleting useless network "{}"'.format(existing_network))
      (success, taskuuid) = session.delete_network(existing_network)
      if not success:
        raise Exception('Error happens on getting existing networks.')

    # Hypervisor
    (success, hypervisor) = session.get_hypervisor()
    if not success:
      raise Exception('Error happens on getting hypervisor.')

    # add new network
    task_list = []
    for network in networks:
      name = network[0]
      if name in existing_networks:
        continue

      print('  Creating network "{}"'.format(name))
      if len(network) == 2:
        (name, vlan) = network
        (success, taskuuid) = session.create_network(name, vlan)
        if not success:
          raise Exception('Error happens on creating network "{}"'.format(name))
      else:
        (ip, vlan, network, prefix, gateway, dns, pools) = network
        if hypervisor != 'AHV':
          (success, taskuuid) = session.create_network(name, vlan)
          if not success:
            raise Exception('Error happens on creating network "{}"'.format(name))
        else:
          (success, taskuuid) = session.create_network_managed(name, vlan, network, prefix, gateway, pools, dns)
          if not success:
            raise Exception('Error happens on creating network "{}"'.format(name))

      task_list.append(taskuuid)

    # wait till end
    wait_tasks(session, task_list)

  def setup_image(session, images):
    images = []
    for (name, config_image) in cluster['images'].items():
      images.append((name, config_image['container'], config_image['url']))

    # check whether container exist or not
    (success, containers) = session.get_container_names()
    if not success:
      raise Exception('Error happens on checking container existance.')

    # get existing images
    (success, existing_images) = session.get_image_names()
    if not success:
      raise Exception('Error happens on getting existing images names.')
    print('  Existing images "{}"'.format(existing_images))

    # upload images which doesn't exist
    task_list = []
    for (image_name, image_container, image_url) in images:
      if image_name in existing_images:
        continue
      if image_container not in containers:
        print('  Failed. container "{}" does not exist on the cluster.'.format(image_container))
        exit(-1)

      print('  Request uploading {} : {}'.format(image_name, image_url))
      (success, taskuuid) = session.upload_image(image_url, image_container, image_name)
      if not success:
        raise Exception('Error happens on uploading image.')
      task_list.append(taskuuid)

    # wait till end
    wait_tasks(session, task_list)

  def _wait_tasks(self, uuids, interval=5):
    first = True
    while(True):
      (success, tasks) = session.get_tasks_status()
      if not success:
        print(tasks)
        continue
        #raise Exception('Error happens on getting tasks status.')

      finished = True
      for task in tasks:
        if task['uuid'] in uuids:
          if first:
            print('Wait till all tasks end. Polling interval {}s.'.format(interval))
            first = False
          print('{} {}% : {}'.format(task['method'], task['percent'], task['uuid']))
          finished = False
        else:
          # Child or other task
          pass

      if finished:
        break
      else:
        print('--')
      time.sleep(interval)

    if not first:
      print('All tasks end.')



class GotoException(Exception):
  pass

class ErrorException(Exception):
  pass

if __name__ == '__main__':
  try:
    args = sys.argv
    del args[0]
    (action, segment, cluster, foundation_vm, nos_package) = get_actions(args)

    if action == 'check':
      check(foundation_vm, segment, cluster)

    elif action == 'foundation':
      foundation(foundation_vm, segment, cluster, nos_package)
      eula(segment, cluster)
      setup(segment, cluster)

    elif action == 'eula':
      eula(segment, cluster)
      setup(segment, cluster)

    elif action == 'setup':
      setup(segment, cluster)

    else:
      # should not be called
      print('Error: Unsupported Action "{}"'.format(action))
      raise ErrorException()

  except GotoException:
    pass

  except ErrorException:
    pass

  except Exception:
    print(traceback.format_exc())
