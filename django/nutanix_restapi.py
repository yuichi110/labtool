'''
Python wrapper for Nutanix REST API.

Author: Yuichi Ito
Email: yuichi.ito@nutanix.com
'''

import paramiko
import requests
from requests.exceptions import RequestException

import json
import traceback
import logging
import datetime

import urllib3
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)


###
### Foundation Client
###

class NutanixFoundationClient:

  @staticmethod
  def create_logger(log_file, level=logging.INFO):
    logger = logging.getLogger('NutanixFoundationClientLogger')
    logger.setLevel(level)
    handler = logging.FileHandler(log_file)  
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
    return logger


  def __init__(self, ip, username, password, logger=None, timeout_connection=5, timeout_read=3600):
    TIMEOUT = (timeout_connection, timeout_read)

    # Test IP and Port reachability
    is_port_open = True
    import socket
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(timeout_connection) # seconds
      s.connect((ip, 8000))
      s.shutdown(2)
    except Exception as e:
      is_port_open = False
    if not is_port_open:
      raise Exception('Unable to connect Nutanix Cluster "{}". Please check ip and port.'.format(ip))

    # Make session
    session = requests.Session()
    session.auth = (username, password)
    session.verify = False                              
    session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

    response = session.get('http://{}:8000/foundation/version'.format(ip), timeout=TIMEOUT)
    if not response.ok:
      raise Exception('Able to connect, but unable to login. Please check credential.')

    def logging_rest(response):
      if logger is None:
        return
      logger.info('======== {} ========'.format(datetime.datetime.now()))
      logger.info('\n * Request * \n')
      logger.info('{} {}'.format(response.request.method, response.request.url))
      for (key, value) in response.request.headers.items():
        logger.debug('{}: {}'.format(key, value))
      logger.debug('')
      if response.request.body:
        try:
          indented_json = json.dumps(json.loads(response.request.body), indent=2)
          logger.info(indented_json)
        except:
          logger.info(response.request.body)
      logger.info('')

      logger.info('\n * Response * \n')
      logger.info('{}'.format(response.status_code))
      for (key, value) in response.headers.items():
        logger.debug('{}: {}'.format(key, value))
      logger.debug('')
      if response.text:
        try:
          indented_json = json.dumps(json.loads(response.text), indent=2)
          logger.info(indented_json)
        except:
          logger.info(response.request.text)
      logger.info('\n\n')

    def logging_error(error_dict):
      if logger is None:
        return
      logger.error('======== {} ========'.format(datetime.datetime.now()))
      logger.error(error_dict['error'])
      if 'stacktrace' in error_dict:
        logger.error('')
        logger.error(error_dict['stacktrace'])
      logger.error('\n\n')

    def handle_error(error, error_dict):
      error_dict['error'] = str(error)
      if not isinstance(error, IntendedException):
        error_dict['stacktrace'] = traceback.format_exc()
      logging_error(error_dict)
      print(error_dict)
    self._handle_error = handle_error

    def get(url, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.get('http://{}:8000/foundation{}'.format(ip, url), timeout=TIMEOUT)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._get = get

    def post(url, body_dict, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.post('http://{}:8000/foundation{}'.format(ip, url), data=json.dumps(body_dict, indent=2), timeout=TIMEOUT)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._post = post

    def reset_state():
      error_dict = {}
      try:
        response = session.get('http://{}:8000/foundation/reset_state'.format(ip), timeout=TIMEOUT)
        if not response.ok:
          error_dict['method'] = response.request.method
          error_dict['url'] = response.request.url
          error_dict['code'] = response.status_code
          error_dict['text'] = response.text
          raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
        # only this API doesn't returns json but blank. 
        return (True, {})
      except Exception as exception:
        self._handle_error(exception, error_dict)
        return (False, error_dict)
    self.reset_state = reset_state

    def abort_session():
      error_dict = {}
      try:
        response = session.post('http://{}:8000/foundation/abort_session'.format(ip), timeout=TIMEOUT)
        if not response.ok:
          error_dict['method'] = response.request.method
          error_dict['url'] = response.request.url
          error_dict['code'] = response.status_code
          error_dict['text'] = response.text
          raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
        # only this API doesn't returns json but blank. 
        return (True, {})
      except Exception as exception:
        self._handle_error(exception, error_dict)
        return (False, error_dict)
    self.abort_session = abort_session
   
    def get_version():
      error_dict = {}
      try:
        response = session.get('http://{}:8000/foundation/version'.format(ip), timeout=TIMEOUT)
        if not response.ok:
          error_dict['method'] = response.request.method
          error_dict['url'] = response.request.url
          error_dict['code'] = response.status_code
          error_dict['text'] = response.text
          raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
        return (True, response.text)
      except Exception as exception:
        self._handle_error(exception, error_dict)
        return (False, error_dict)
    self.get_version = get_version

    def does_mac_exist(mac_address, nic):
      words = mac_address.split(':')
      # add 0 on each octets if it is missed
      for i in range(len(words)):
        if len(words[i]) == 0:
          words[i] = '0' + words[i]
      # reverse 7th bit on first octet
      w0 = bin(int(words[0], 16))[2:]
      w0 = '0' * (8-len(w0)) + w0
      if w0[6] == '0':
        w0 = w0[:6] + '1' + w0[7]
      else:
        w0 = wo[:6] + '0' + w0[7]
      words[0] = hex(int(w0, 2))[2:]
      # make ipv6 link local address
      linklocal_address = 'fe80::{}{}:{}ff:fe{}:{}{}'.format(*words)

      # make paramiko session
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(ip, username=username, password=password)

      # try ping and checking mac address existance
      command = 'ping6 -I {} {} -c 3'.format(nic, linklocal_address)
      stdin, stdout, stderr = client.exec_command(command)
      exist = False
      for line in stdout:
        if 'packets transmitted' in line:
          if not '0 received' in line:
            exist = True
          break
      client.close()
      return exist
    self.does_mac_exist = does_mac_exist

    def get_mac_from_ip(ip_address):
      client = paramiko.SSHClient()
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(ip, username=username, password=password)
      command = 'ping {} -c 3'.format(ip_address)
      stdin, stdout, stderr = client.exec_command(command)
      exist = False
      for line in stdout:
        if 'packets transmitted' in line:
          if not '0 received' in line:
            exist = True
          break
      if not exist:
        return ''

      stdin, stdout, stderr = client.exec_command('/sbin/arp')
      for line in stdout:
        if ip_address in line:
          words = line.split()
          return words[2]
      client.close()
      return ''
    self.get_mac_from_ip = get_mac_from_ip

  def get_nos_packages(self):
    error_dict = {}
    try:
      response_dict = self._get('/enumerate_nos_packages', error_dict)
      return (True, response_dict)
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def get_nics(self):
    error_dict = {}
    try:
      response_dict = self._get('/list_nics', error_dict)
      return (True, response_dict)
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def choose_primary_nic(self, nic):
    error_dict = {}
    try:
      body_dict = {
        "primary_nic": nic
      }
      response_dict = self._post('/primary_nic', body_dict, error_dict)
      return (True, response_dict)
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def discover_nodes(self):
    error_dict = {}
    try:
      response_dict = self._get('/discover_nodes')
      return (True, response_dict)
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def get_progress(self):
    error_dict = {}
    try:
      response_dict = self._get('/progress', error_dict)
      return (True, response_dict)
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def ipmi_config(self, 
    netmask, gateway, # page1
    nodeinfo_list,    # page2
    cluster_name, external_ip, name_server, ntp_server, # page3
    nos_package # page4
    ):
    error_dict = {}
    try:
      body_dict = self._get_jsonbody(netmask, gateway, nodeinfo_list,
        cluster_name, external_ip, name_server, ntp_server, nos_package)
      response_dict = self._post('/ipmi_config', body_dict, error_dict)
      return (True, response_dict)
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def pre_check(self, 
    netmask, gateway, # page1
    nodeinfo_list,    # page2
    cluster_name, external_ip, name_server, ntp_server, # page3
    nos_package # page4
    ):
    error_dict = {}
    try:
      body_dict = self._get_jsonbody(netmask, gateway, nodeinfo_list,
        cluster_name, external_ip, name_server, ntp_server, nos_package)
      response_dict = self._post('/pre_check', body_dict, error_dict)
      return (True, response_dict)
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def image_nodes(self, 
    netmask, gateway, # page1
    nodeinfo_list,    # page2
    cluster_name, external_ip, name_server, ntp_server, # page3
    nos_package # page4
    ):
    error_dict = {}
    try:
      body_dict = self._get_jsonbody(netmask, gateway, nodeinfo_list,
        cluster_name, external_ip, name_server, ntp_server, nos_package)
      response_dict = self._post('/image_nodes', body_dict, error_dict)
      return (True, response_dict)
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def _get_jsonbody(self, 
    netmask, gateway, # page1
    nodeinfo_list,    # page2
    cluster_name, external_ip, name_server, ntp_server, # page3
    nos_package # page4
    ):
    body_dict = {
      "ui_skip_network_setup": True, 
      "cvm_gateway": gateway, 
      "ui_nic": "eth0", 
      "blocks": [
        {
          "ui_test_name": "Manual-1", 
          "block_id":None,
          "ui_block_id":"",
          "nodes": []
        }
      ],
      "ui_is_installing_secondary_hypervisor": False, 
      "hypervisor_netmask": netmask, 
      "bond_lacp_rate": None, 
      "ipmi_netmask": netmask, 
      "ui_is_installing_cvm": True, 
      "hyperv_sku": None, 
      "ui_have_vlan": False, 
      "bond_mode": "", 
      "cvm_netmask": netmask, 
      "nos_package": nos_package, 
      "hypervisor_gateway": gateway, 
      "hypervisor_iso": {
        "kvm": {
          "checksum": None, 
          "filename": "AHV bundled with AOS (version 4.6+)"
        }
      }, 
      "ipmi_gateway": gateway, 
      "clusters": [
        {
          "cluster_external_ip": external_ip, 
          "cluster_init_successful": None, 
          "redundancy_factor": 2, 
          "cluster_name": cluster_name, 
          "cvm_ntp_servers": ntp_server, 
          "cluster_members": [], 
          "timezone": "Asia/Tokyo", 
          "cvm_dns_servers": name_server, 
          "cluster_init_now": True
        }
      ], 
      "hypervisor": "kvm", 
      "ui_is_installing_hypervisor": True
    }  

    for (ipmi_mac, ipmi_ip, host_ip, cvm_ip, host_name, position) in nodeinfo_list:
      # add cluster member
      cluster_members = body_dict['clusters'][0]['cluster_members']
      cluster_members.append(cvm_ip)
      # add node
      node_info = {
        "ipv6_address": None, 
        "is_bare_metal": True, 
        "image_successful": None, 
        "image_now": True, 
        "ipv6_interface": None, 
        "nos_version": "99.0", 
        "ipmi_ip": ipmi_ip, 
        "hardware_attributes_override": {}, 
        "node_position": position.upper(), 
        "is_selected": True, 
        "hypervisor_hostname": host_name, 
        "cvm_gb_ram": 32, 
        "compute_only": False, 
        "ipmi_password": "ADMIN", 
        "ipmi_configure_now": True, 
        "hypervisor_ip": host_ip, 
        "ipmi_user": "ADMIN", 
        "ipmi_mac": ipmi_mac, 
        "hypervisor": "kvm", 
        "cvm_ip": cvm_ip
      }
      nodes = body_dict['blocks'][0]['nodes']
      nodes.append(node_info)

    return body_dict


###
### REST API Client
###

class NutanixRestApiClient:
  @staticmethod
  def create_logger(log_file, level=logging.INFO):
    logger = logging.getLogger('NutanixRestApiClientLogger')
    logger.setLevel(level)
    handler = logging.FileHandler(log_file)  
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)
    return logger

  @staticmethod
  def change_default_system_password(ip, old_password, new_password):
    # Make session without auth
    session = requests.Session()
    session.verify = False                 
    session.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    body_dict = {
      "oldPassword":old_password,
      "newPassword":new_password
    }
    response = session.post('https://{}:9440/api/nutanix/v1/utils/change_default_system_password'.format(ip), 
      data=json.dumps(body_dict, indent=2))

    if response.ok:
      return (True, response.json())
    else:
      error_dict = {}
      error_dict['method'] = response.request.method
      error_dict['url'] = response.request.url
      error_dict['code'] = response.status_code
      error_dict['text'] = response.text
      return (False, error_dict)

  def __init__(self, ip, username, password, logger=None, timeout_connection=5, timeout_read=15):
    TIMEOUT = (timeout_connection, timeout_read)

    # Test IP and Port reachability
    is_port_open = True
    import socket
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(timeout_connection) # seconds
      s.connect((ip, 9440))
      s.shutdown(2)
    except Exception as e:
      is_port_open = False
    if not is_port_open:
      raise Exception('Unable to connect Nutanix Cluster "{}". Please check ip and port.'.format(ip))

    # Make session
    session = requests.Session()
    session.auth = (username, password)
    session.verify = False                              
    session.headers.update({'Content-Type': 'application/json; charset=utf-8'})

    # Test session
    is_requests_ok = True
    url = 'https://{}:9440/PrismGateway/services/rest/v1/cluster'.format(ip)
    try:
      resp = session.get(url, timeout=TIMEOUT)
    except:
      is_requests_ok = False
    if not is_requests_ok:
      raise Exception('Able to access. But unexpected error happens. Please check server status.')
    if not resp.ok:
      raise Exception('Able to access. But unable to get cluster info. Please check your credential.')


    ###
    ### Debug utility for CRUD functions
    ###

    def logging_rest(response):
      if logger is None:
        return
      logger.info('======== {} ========'.format(datetime.datetime.now()))
      logger.info('\n * Request * \n')
      logger.info('{} {}'.format(response.request.method, response.request.url))
      for (key, value) in response.request.headers.items():
        logger.debug('{}: {}'.format(key, value))
      logger.debug('')
      if response.request.body:
        try:
          indented_json = json.dumps(json.loads(response.request.body), indent=2)
          logger.info(indented_json)
        except:
          logger.info(response.request.body)
      logger.info('')

      logger.info('\n * Response * \n')
      logger.info('{}'.format(response.status_code))
      for (key, value) in response.headers.items():
        logger.debug('{}: {}'.format(key, value))
      logger.debug('')
      if response.text:
        try:
          indented_json = json.dumps(json.loads(response.text), indent=2)
          logger.info(indented_json)
        except:
          logger.info(response.request.text)
      logger.info('\n\n')


    def logging_error(error_dict):
      if logger is None:
        return
      logger.error('======== {} ========'.format(datetime.datetime.now()))
      logger.error(error_dict['error'])
      if 'stacktrace' in error_dict:
        logger.error('')
        logger.error(error_dict['stacktrace'])
      logger.error('\n\n')

    ###
    ### Make CRUD utility private methods with closure.
    ### To avoid being modifyied session and ip etc from outside.
    ###

    # API v0.8

    def get_v08(url, error_dict):
      if not url.startswith('/'): url = '/' + url
      attempts = 0
      while attempts < 3:
        try:
          response = session.get('https://{}:9440/api/nutanix/v0.8{}'.format(ip, url), timeout=TIMEOUT)
          break
        except RequestException as e:
          logger.error(e)
          logger.error('retly')
          attempts += 1
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._get_v08 = get_v08

    def post_v08(url, body_dict, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.post('https://{}:9440/api/nutanix/v0.8{}'.format(ip, url), data=json.dumps(body_dict, indent=2), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._post_v08 = post_v08

    def put_v08(url, body_dict, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.put('https://{}:9440/api/nutanix/v0.8{}'.format(ip, url), data=json.dumps(body_dict, indent=2), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._put_v08 = put_v08

    def delete_v08(url, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.delete('https://{}:9440/api/nutanix/v0.8{}'.format(ip, url), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      try:
        return response.json()
      except:
        return {}
    self._delete_v08 = delete_v08


    # API v1

    def get_v1(url, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.get('https://{}:9440/api/nutanix/v1{}'.format(ip, url), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._get_v1 = get_v1

    def post_v1(url, body_dict, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.post('https://{}:9440/api/nutanix/v1{}'.format(ip, url), data=json.dumps(body_dict, indent=2), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._post_v1 = post_v1

    def put_v1(url, body_dict, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.put('https://{}:9440/api/nutanix/v1{}'.format(ip, url), data=json.dumps(body_dict, indent=2), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._put_v1 = put_v1

    def delete_v1(url, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.delete('https://{}:9440/api/nutanix/v1{}'.format(ip, url), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      try:
        return response.json()
      except:
        return {}
    self._delete_v1 = delete_v1


    # API v2

    def get_v2(url, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.get('https://{}:9440/api/nutanix/v2.0{}'.format(ip, url), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._get_v2 = get_v2

    def post_v2(url, body_dict, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.post('https://{}:9440/api/nutanix/v2.0{}'.format(ip, url), data=json.dumps(body_dict, indent=2), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._post_v2 = post_v2

    def put_v2(url, body_dict, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.put('https://{}:9440/api/nutanix/v2.0{}'.format(ip, url), data=json.dumps(body_dict, indent=2), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      return response.json()
    self._put_v2 = put_v2

    def delete_v2(url, error_dict):
      if not url.startswith('/'): url = '/' + url
      response = session.delete('https://{}:9440/api/nutanix/v2.0{}'.format(ip, url), timeout=TIMEOUT)
      logging_rest(response)
      if not response.ok:
        error_dict['method'] = response.request.method
        error_dict['url'] = response.request.url
        error_dict['code'] = response.status_code
        error_dict['text'] = response.text
        raise IntendedException('Receive unexpected response code "{}".'.format(response.status_code))
      try:
        return response.json()
      except:
        return {}
    self._delete_v2 = delete_v2


    # Error handling

    def handle_error(error, error_dict):
      error_dict['error'] = str(error)
      if not isinstance(error, IntendedException):
        error_dict['stacktrace'] = traceback.format_exc()
      logging_error(error_dict)
    self._handle_error = handle_error



  ###
  ### Hackathon
  ###

  def get_ipmi_host_cvm_ips(self):
    error_dict = {}
    try:
      response_dict = self._get_v2('/hosts', error_dict)
      host_list = []
      cvm_list = []
      ipmi_list = []
      for entity in response_dict['entities']:
        host_list.append(entity.get('hypervisor_address'))
        cvm_list.append(entity.get('controller_vm_backplane_ip'))
        ipmi_list.append(entity.get('ipmi_address'))
      return (True, (ipmi_list, host_list, cvm_list))

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def get_agent_vms(self):
    error_dict = {}
    try:
      response_dict = self._get_v2('/vms/?include_vm_nic_config=true', error_dict)
      agentvm_list = []
      for entity in response_dict['entities']:
          is_agent_vm = entity['vm_features']["AGENT_VM"]
          if is_agent_vm == True:
            #print("Found agent VM : {}".format(entity.get('name')))
            agentvm_list.append(entity['name'])
      return (True, agentvm_list)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def get_poweredon_vms(self):
    error_dict = {}
    try:
      response_dict = self._get_v2('/vms/?include_vm_nic_config=true', error_dict)
      vm_list = []
      for entity in response_dict['entities']:
        if(entity.get('power_state') == 'on'):
          vm_list.append(entity.get('name'))
      return (True, vm_list)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def get_vm_powerstate(self, vm_name):
    error_dict = {}
    try:
      response_dict = self._get_v2('/vms', error_dict)
      for vm in response_dict['entities']:
        if vm['name'] != vm_name:
          continue
        return (True, vm['power_state'])
      raise IntendedException('Error. Unable to find the vm "{}"'.format(name))

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def get_pc_vms(self):
    error_dict = {}
    try:
      response_list = self._get_v1('/multicluster/cluster_external_state', error_dict)
      pc_ip_list = []
      for response in response_list:
        pc_ip_list.append(response.get('clusterDetails').get('ipAddresses')[0])

      pc_name_list = []
      response_dict = self._get_v2('/vms/?include_vm_nic_config=true', error_dict)
      for entity in response_dict['entities']:
        if len(entity.get('vm_nics')) > 0:
          try:
            vm_ip = entity.get('vm_nics')[0].get('ip_address')
            if vm_ip in pc_ip_list:
              pc_name_list.append(entity.get('name'))
          except:
            pass
      return (True, pc_name_list)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def get_fsvms(self):
    error_dict = {}
    try:
      response_dict = self._get_v1('/vfilers', error_dict)
      fsvm_list = []
      for entity in response_dict['entities']:
        for nvms in entity['nvms']:
          fsvm_list.append(nvms['name'])
      return (True, fsvm_list)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def get_vm_ip(self, vm_name):
    error_dict = {}
    try:
      response_dict = self._get_v2('/vms/?include_vm_nic_config=true', error_dict)
      for vm in response_dict['entities']:
        if vm['name'] != vm_name:
          continue
        if len(vm['vm_nics']) == 0:
          continue
        try:
          return (True, vm['vm_nics'][0]['ip_address'])
        except:
          pass
      raise IntendedException('Error. Unable to find the vm "{}"'.format(name))

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  ###
  ### Developing now
  ###

  def make_pc(self, version, container, ip, network, subnetmask, gateway):
    pass
    '''
    Request URL: https://10.149.161.41:9440/api/nutanix/v3/prism_central
    Request Method: POST

    Payload
    {
       "resources":{
          "version":"5.10.3",
          "should_auto_register":false,
          "pc_vm_list":[
             {
                "vm_name":"PrismCentral",
                "container_uuid":"0fc0176b-7eac-4fb0-a27d-9069bc3cf371",
                "num_sockets":4,
                "data_disk_size_bytes":536870912000,
                "memory_size_bytes":17179869184,
                "dns_server_ip_list":[
                   "8.8.8.8"
                ],
                "nic_list":[
                   {
                      "ip_list":[
                         "10.149.161.42"
                      ],
                      "network_configuration":{
                         "network_uuid":"a134b6d8-6e4d-4dea-9aa3-c6d225ffdb3b",
                         "subnet_mask":"255.255.252.0",
                         "default_gateway":"10.149.160.1"
                      }
                   }
                ]
             }
          ]
       }
    }
    '''

  def register_pc(self):
    pass
    '''
    https://10.149.161.41:9440/PrismGateway/services/rest/v1/multicluster/add_to_multicluster
    Request Method: POST
    Status Code: 200 OK

    {
       "ipAddresses":[
          "10.149.161.42"
       ],
       "username":"admin",
       "password":"Nutanix/4u!"
    }
    '''


  def set_eula(self, user_name, company_name, job_title):
    error_dict = {}
    try:
      body_dict = {
        "username":"yuichi",
        "companyName":"nutanix",
        "jobTitle":"se"
      }
      response_dict = self._post_v1('/eulas/accept', body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def set_initial_pulse(self):
    error_dict = {}
    try:
      body_dict = {
        "emailContactList":None,
        "enable":False,
        "verbosityType":None,
        "enableDefaultNutanixEmail":False,
        "defaultNutanixEmail":None,
        "nosVersion":None,
        "isPulsePromptNeeded":False,
        "remindLater":None
      }
      response_dict = self._put_v1('/pulse', body_dict, error_dict)
      return (True, response_dict)
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def set_initial_alerts(self):
    error_dict = {}
    try:
      body_dict = {
        "enableDefaultNutanixEmail":False
      }
      response_dict = self._put_v1('/alerts/configuration', body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def change_password(self, old_password, new_password):
    error_dict = {}
    try:
      body_dict = {
        "oldPassword":old_password,
        "newPassword":new_password
      }
      response_dict = self._put_v1('/users/change_password', body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)



  def change_language(self, language):
    error_dict = {}
    try:
      if language not in ['en-US', 'ja-JP', 'zh-CN']:
        raise Exception('Error: language must be one of them "en-US", "ja-JP", "zh-CN"')
      
      body_dict = {
        "username":"admin",
        "locale":language,
      }
      response_dict = self._put_v1('/users/admin/profile', body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)
      

  def add_fs_whitelist(self, network, subnetmask):
    error_dict = {}
    try:
      body_dict = ['{}/{}'.format(network, subnetmask)]
      response_dict = self._post_v1('/cluster/nfs_whitelist/add_list', body_dict, error_dict)
      return (True, response_dict)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def change_autologout_minute(self, user_timeout, system_timeout):
    error_dict = {}
    try:
      user_timeout = user_timeout * 60 * 1000
      system_timeout = system_timeout * 60 * 1000

      # user_data
      body_dict = {
        "type":"UI_CONFIG",
        "key":"autoLogoutTime",
        "username":"admin",
        "value":user_timeout
      }
      response_dict = self._put_v1('/application/user_data', body_dict, error_dict)

      body_dict = {
        "type":"ui_config",
        "key":"autoLogoutGlobal",
        "value":system_timeout
      }
      response_dict = self._put_v1('/application/system_data', body_dict, error_dict)

      body_dict = {
        "type":"ui_config",
        "key":"autoLogoutOverride",
        "value":0
      }
      response_dict = self._put_v1('/application/system_data', body_dict, error_dict)
      return (True, {})

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  ###
  ### Cluster Operation
  ###

  def get_cluster_info(self):
    error_dict = {}
    try:
      response_dict = self._get_v1('/cluster/', error_dict)
      return_dict = {
        # Basic
        'uuid' : response_dict['uuid'],
        'name' : response_dict['name'],
        'timezone' : response_dict['timezone'],
        'is_lts' : response_dict['isLTS'],
        'version' : response_dict['version'],
        'version_ncc' : response_dict['nccVersion'],

        # RF
        'current_redundancy_factor' : response_dict['clusterRedundancyState']['currentRedundancyFactor'],
        'desired_redundancy_factor' : response_dict['clusterRedundancyState']['desiredRedundancyFactor'],

        # Network
        'ip_external' : response_dict['clusterExternalIPAddress'],
        'ip_iscsi' : response_dict['clusterExternalDataServicesIPAddress'],
        'network_external' : response_dict['externalSubnet'],
        'network_internal' : response_dict['internalSubnet'],
        'nfs_whitelists' : response_dict['globalNfsWhiteList'],

        # Node and Block
        'num_nodes' : response_dict['numNodes'],
        'block_serials' : response_dict['blockSerials'],
        'num_blocks' : len(response_dict['blockSerials']),

        # Servers
        'name_servers' : response_dict['nameServers'],
        'ntp_servers' : response_dict['ntpServers'],
        'smtp_server' : '' if response_dict['smtpServer'] is None else response_dict['smtpServer'],

        # Storage
        'storage_type' : response_dict['storageType'],
      }

      hypervisors = response_dict['hypervisorTypes']
      if len(hypervisors) == 1:
        return_dict['hypervisor'] = hypervisors[0]
        if return_dict['hypervisor'] == 'kKvm':
          return_dict['hypervisor'] = 'AHV'
      else:
        # needs update here
        return_dict['hypervisor'] = 'unknown'

      return (True, return_dict)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def get_cluster_name(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['name'])
    return (success, dict)

  def change_cluster_name(self):
    return {'error':'Error: Not supported now'}

  def get_hypervisor(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['hypervisor'])
    return (success, dict)

  def get_version(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['version'])
    return (success, dict)

  def get_name_servers(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['name_servers'])
    return (success, dict)

  def get_ntp_servers(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['ntp_servers'])
    return (success, dict)

  def get_block_serials(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['block_serials'])
    return (success, dict)

  def get_num_nodes(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['num_nodes'])
    return (success, dict)

  def get_desired_redundancy_factor(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['desired_redundancy_factor'])
    return (success, dict)

  def get_current_redundancy_factor(self):
    (success, dict) = self.get_cluster_info()
    if success:
      return (success, dict['current_redundancy_factor'])
    return (success, dict)


  ###
  ### Storagepool Operation
  ###

  def get_storagepool_names(self):
    error_dict = {}
    try:
      response_dict = self._get_v1('/storage_pools/', error_dict)
      storagepools = []
      for storagepool in response_dict['entities']:
        storagepools.append(storagepool['name'])
      return (True, storagepools)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  ###
  ### Container Operation
  ###

  def get_container_names(self):
    error_dict = {}
    try:
      response_dict = self._get_v1('/containers/', error_dict)
      container_names = []
      for cont in response_dict['entities']:
        container_names.append(cont['name'])
      return (True, container_names)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def get_container_info(self, name):
    error_dict = {}
    try:
      response_dict = self._get_v1('/containers/', error_dict)
      container_info = {}
      for cont in response_dict['entities']:
        if cont['name'] != name:
          continue
        container_info = {
          'uuid':cont['containerUuid'],
          'id':cont['id'],
          'storagepool_uuid':cont['storagePoolUuid'],
          'usage':cont['usageStats']['storage.usage_bytes']
        }
        break  
      if len(container_info) == 0:
        raise IntendedException('Error. Unable to find container "{}"'.format(name))
      return (True, container_info)
      
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def create_container(self, container_name, storagepool_name=''):
    error_dict = {}
    try:
      # Get storage pool uuid.
      response_dict = self._get_v1('/storage_pools/', error_dict)
      storagepool_dict = {}
      for storagepool in response_dict['entities']:
        storagepool_dict[storagepool['name']] = storagepool['storagePoolUuid']
      storagepool_uuid = ''
      if storagepool_name == '':
        if len(storagepool_dict) != 1:
          raise IntendedException('Error. Needs to provide storagepool name if having 2+ pools.')
        storagepool_uuid = storagepool_dict.popitem()[1]
      else:
        if storagepool_name not in storagepool_dict:
          raise IntendedException('Error. Storagepool name "{}" doesn\'t exist.'.format(storagepool_name))
        storagepool_uuid = storagepool_dict[storagepool_name]

      # Create container
      body_dict = {
        "id": None,
        "name": container_name,
        "storagePoolId": storagepool_uuid,
        "totalExplicitReservedCapacity": 0,
        "advertisedCapacity": None,
        "compressionEnabled": True,
        "compressionDelayInSecs": 0,
        "fingerPrintOnWrite": "OFF",
        "onDiskDedup": "OFF"
      }
      response_dict = self._post_v1('/containers/', body_dict, error_dict)
      return (True, response_dict['value'])

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def update_container(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def delete_container(self, name):
    error_dict = {}
    try:
      # Get uuid from name
      response_dict = self._get_v1('/containers/', error_dict)
      container_uuid = ''
      for cont in response_dict['entities']:
        if cont['name'] == name:
          container_uuid = cont['containerUuid']
          break
      if container_uuid == '':
        raise IntendedException('Error. Unable to find container "{}"'.format(name))

      # Delete
      response_dict = self._delete_v1('/containers/{}'.format(container_uuid), error_dict)
      return (True, response_dict['value'])
      
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  ###
  ### Network Operation
  ###

  def get_network_names(self):
    error_dict = {}
    try:
      response_dict = self._get_v2('/networks/', error_dict)
      network_names = []
      for network in response_dict['entities']:
        network_names.append(network['name'])
      return (True, network_names)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def get_network_info(self, name):
    error_dict = {}
    try:
      response_dict = self._get_v2('/networks/', error_dict)
      network_info = {}
      for network in response_dict['entities']:
        if name != network['name']:
          continue
        network_info = {
          'name' : network['name'],
          'uuid' : network['uuid'],
          'vlan' : network['vlan_id'],
          'managed' : False
        }
        if 'network_address' in network['ip_config']:
          network_info['managed'] = True
          network_info['managed_address'] = network['ip_config']['network_address']
          network_info['managed_prefix'] = network['ip_config']['prefix_length']
          network_info['managed_gateway'] = network['ip_config']['default_gateway']
          network_info['managed_dhcp_address'] = network['ip_config']['dhcp_server_address']
          network_info['managed_dhcp_options'] = network['ip_config']['dhcp_options']
          pools = []
          for pool in network['ip_config']['pool']:
            words = pool['range'].split(' ')
            pools.append((words[0], words[1]))
          network_info['managed_pools'] = pools
        break
      if network_info == {}:
        raise IntendedException('Error. Unable to find network "{}"'.format(name))
      return (True, network_info)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def create_network(self, name, vlan):
    error_dict = {}
    try:
      body_dict = {
        'name' : name,
        'vlan_id' : str(vlan)
      }
      response_dict = self._post_v2('/networks/', body_dict, error_dict)
      return (True, response_dict['network_uuid'])

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def create_network_managed(self, name, vlan, network_address, prefix, gateway, pools, dns=''):
    error_dict = {}
    try:      
      body_dict = {
        'name' : name,
        'vlan_id' : str(vlan),
        'ip_config': {
          'dhcp_options': {
            'domain_name_servers': dns,
          },
          'network_address': network_address,
          'prefix_length': str(prefix),
          'default_gateway': gateway,
          "pool": []
        }
      }
      for (from_ip, to_ip) in pools:
        entity = {'range' : '{} {}'.format(from_ip, to_ip)}
        body_dict['ip_config']['pool'].append(entity)

      response_dict = self._post_v2('/networks/', body_dict, error_dict)
      return (True, response_dict['network_uuid'])

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def is_network_used(self, name):
    error_dict = {}
    try:
      # Get uuid
      response_dict = self._get_v2('/networks/', error_dict)
      network_uuid = ''
      for network in response_dict['entities']:
        if network['name'] == name:
          network_uuid = network['uuid']
          break
      if network_uuid == '':
        raise IntendedException('Error. Unable to find network "{}"'.format(name))

      # Check all VMs whether using this network or not.
      response_dict = self._get_v2('/vms/?include_vm_nic_config=true', error_dict)
      is_used = False
      for vm in response_dict['entities']:
        for nic in vm['vm_nics']:
          if network_uuid == nic['network_uuid']:
            is_used = True
            break
        if is_used:
          break
      return (True, is_used)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def delete_network(self, name):
    error_dict = {}
    try:
      # Get uuid
      response_dict = self._get_v2('/networks/', error_dict)
      network_uuid = ''
      for network in response_dict['entities']:
        if network['name'] == name:
          network_uuid = network['uuid']
          break
      if network_uuid == '':
        raise IntendedException('Error. Unable to find network "{}"'.format(name))

      # Delete
      response_dict = self._delete_v2('/networks/{}'.format(network_uuid), error_dict)
      return (True, None)
      
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def update_network():
    return (False, {'error':'Error. Not supported now.'})


  ###
  ### VM Operation
  ###

  def get_vm_names(self):
    error_dict = {}
    try:
      response_dict = self._get_v2('/vms/', error_dict)
      vm_names = []
      for vm in response_dict['entities']:
        vm_names.append(vm['name'])
      return (True, vm_names)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def get_vm_info(self, name):
    error_dict = {}
    try:
      response_dict = self._get_v2('/vms/?include_vm_disk_config=true&include_vm_nic_config=true', error_dict)
      vm_info = {}
      for vm in response_dict['entities']:
        if vm['name'] != name:
          continue
        vm_info = {
          'name' : vm['name'],
          'uuid' : vm['uuid'],
          'memory_mb' : vm['memory_mb'],
          'num_vcpus' : vm['num_vcpus'],
          'num_cores' : vm['num_cores_per_vcpu'],
          'power_state' : vm['power_state'],
          'timezone' : vm['timezone'],
          'is_agent' : vm['vm_features'].get('AGENT_VM', False)
        }

        disks = []
        for disk in vm['vm_disk_info']:
          disk_info = {
            'bus' : disk['disk_address']['device_bus'],
            'label' : disk['disk_address']['disk_label'],
            'is_cdrom' : disk['is_cdrom'],
            'is_flashmode' : disk['flash_mode_enabled'],
            'is_empty' : disk['is_empty'],
            'vmdisk_uuid' : disk['disk_address'].get('vmdisk_uuid', ''),
            'container_uuid' : disk.get('storage_container_uuid', ''),
            'size' : disk.get('size', 0)
          }
          disks.append(disk_info)
        vm_info['disks'] = disks

        nics = []
        for nic in vm['vm_nics']:
          nic_info = {
            'mac_address' : nic['mac_address'],
            'network_uuid' : nic['network_uuid'],
            'is_connected' : nic['is_connected']
          }
        vm_info['nics'] = nics
        break
      if vm_info == {}:
        raise IntendedException('Error. Unable to find vm "{}"'.format(name))
      return (True, vm_info)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)

  def clone_vm(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def create_vm_new(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def create_vm_from_image(self, name, memory_mb, num_vcpus, num_cores, image_name, network_name, ip_address=''):
    error_dict = {}
    try:
      # image uuid
      response_dict = self._get_v2('/images/', error_dict)
      vmdisk_uuid = ''
      vmdisk_size = 0
      for image in response_dict['entities']:
        if image['name'] == image_name:
          vmdisk_uuid = image['vm_disk_id']
          vmdisk_size = image['vm_disk_size']
          break
      if vmdisk_uuid == '':
        raise IntendedException('Error. Unable to find image "{}"'.format(image_name))

      # network uuid
      response_dict = self._get_v2('/networks/', error_dict)
      network_uuid = ''
      for network in response_dict['entities']:
        if network['name'] == network_name:
          network_uuid = network['uuid']
          break
      if network_uuid == '':
        raise IntendedException('Error. Unable to find network "{}"'.format(name))

      # create vm with image_uuid and network_uuid
      body_dict = {
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
        "affinity": None,
        "vm_features": {
          "AGENT_VM": False
        }
      }
      if ip_address == '':
        del body_dict['vm_nics'][0]['requested_ip_address']
      response_dict = self._post_v2('/vms/', body_dict, error_dict)
      return (True, response_dict['task_uuid'])

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def update_vm(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def delete_vm(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def poweron_vm(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def poweroff_vm(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def shutdown_vm(self, name):
    return (False, {'error':'Error. Not supported now.'})

  def snapshot_vm(self, vm_name, snapshot_name):
    return (False, {'error':'Error. Not supported now.'})


  ###
  ### Vdisk Operation
  ###

  def get_vm_disks(self, vm_name):
    error_dict = {}
    try:
      response_dict = self._get_v2('/vms/?include_vm_disk_config=true', error_dict)
      for vm in response_dict['entities']:
        if vm['name'] != vm_name:
          continue
        vdisks = []
        for vdisk in vm['vm_disk_info']:
          if vdisk['is_cdrom']:
            continue
          vdisks.append(vdisk['disk_address']['disk_label'])
        return (True, vdisks)
      raise IntendedException('Error. Unable to find the vm "{}"'.format(name))

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  ###
  ### Image Operation
  ###

  def get_image_names(self):
    error_dict = {}
    try:
      response_dict = self._get_v08('/images/', error_dict)
      image_names = []
      for image in response_dict['entities']:
        image_names.append(image['name'])
      return (True, image_names)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def upload_image(self, file_url, target_container, image_name):
    error_dict = {}
    try:
      # Get container UUID
      response_dict = self._get_v1('/containers/', error_dict)
      target_container_uuid = ''
      for cont in response_dict['entities']:
        if cont['name'] == target_container:
          target_container_uuid = cont['containerUuid']
          break
      if target_container_uuid == '':
        raise IntendedException('Unable to find container "{}"'.format(target_container))

      # Upload
      is_iso = file_url.lower().endswith('.iso')
      image_type = 'ISO_IMAGE' if is_iso else 'DISK_IMAGE'
      body_dict = {
        "name": image_name,
        "annotation": "",
        "imageType": image_type,
        "imageImportSpec": {
          "containerUuid": target_container_uuid,
          "url": file_url,
        }
      }
      response_dict = self._post_v08('/images/', body_dict, error_dict)
      return (True, response_dict['taskUuid'])

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def create_image_from_vm_vdisk(self, vm_name, vm_disk, target_container, image_name):
    error_dict = {}
    try:
      # Get vdisk_uuid and source_container_uuid
      response_dict = self._get_v2('/vms/?include_vm_disk_config=true', error_dict)
      vdisk_uuid = ''
      source_container_uuid = ''
      for vm in response_dict['entities']:
        if vm['name'] != vm_name:
          continue
        for vdisk in vm['vm_disk_info']:
          if vdisk['disk_address']['disk_label'] != vm_disk:
            continue
          vdisk_uuid = vdisk['disk_address']['vmdisk_uuid']
          source_container_uuid = vdisk['storage_container_uuid']
          break
        break
      if vdisk_uuid == '':
        raise Exception('Error: Unable to find VM "{}" which has vDisk "{}"'.format(vm_name, vm_disk))

      # Get souce_container_name and target_container_uuid
      response_dict = self._get_v1('/containers/', error_dict)
      source_container_name = ''
      target_container_uuid = ''
      for cont in response_dict['entities']:
        if cont['containerUuid'] == source_container_uuid:
          source_container_name = cont['name']
        if cont['name'] == target_container:
          target_container_uuid = cont['containerUuid']
      if source_container_name == '':
        raise IntendedException('Error: Unable to find source container name from uuid="{}".'.format(source_container_uuid))
      if target_container_uuid == '':
        raise IntendedException('Error: Unable to find container "{}"'.format(target_container))

      # Upload image from VM vDisk
      nfs_url = 'nfs://127.0.0.1/{}/.acropolis/vmdisk/{}'.format(source_container_name, vdisk_uuid)
      body_dict = {
        "name": image_name,
        "annotation": "",
        "imageType": 'DISK_IMAGE',
        "imageImportSpec": {
          "containerUuid": target_container_uuid,
          "url": nfs_url,
        }
      }
      response_dict = self._post_v08('/images/', body_dict, error_dict)
      return (True, response_dict['taskUuid'])
      
    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def delete_image(self, name):
    error_dict = {}
    try:
      # Get image UUID
      response_dict = self._get_v08('/images/', error_dict)
      image_uuid = ''
      for image in response_dict['entities']:
        if image['name'] == name:
          image_uuid = image['uuid']
          break
      if image_uuid == '':
        raise IntendedException('Error: Unable to find image "{}"'.format(name))

      # Delete
      response_dict = self._delete_v08('/images/{}'.format(image_uuid), error_dict)
      return (True, response_dict['taskUuid'])

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  ###
  ### Task Operation
  ###

  def get_task_status(self, task_uuid):
    error_dict = {}
    try:
      response_dict = self._get_v08('/tasks/{}'.format(task_uuid), error_dict)
      return_dict = {
        'uuid': response_dict['uuid'],
        'method': response_dict['metaRequest']['methodName'],
        'percent': response_dict.get('percentageComplete', 0),
        'status': response_dict['progressStatus'],
      }
      return (True, return_dict)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


  def get_tasks_status(self):
    error_dict = {}
    try:
      response_dict = self._get_v08('/tasks/?includeCompleted=false', error_dict)
      task_list = []
      for entity in response_dict['entities']:
        entity_dict = {
          'uuid': entity['uuid'],
          'method': entity['metaRequest']['methodName'],
          'percent': entity.get('percentageComplete', 0),
          'status': entity['progressStatus'],
        }
        task_list.append(entity_dict)
      return (True, task_list)

    except Exception as exception:
      self._handle_error(exception, error_dict)
      return (False, error_dict)


###
### Custome Exception Classes
###

class IntendedException(Exception):
  pass