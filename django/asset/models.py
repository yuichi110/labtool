from django.db import models
from django.core.exceptions import ValidationError

import uuid
import json

class Asset(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100, unique=True)
  data = models.TextField()

  def __str__(self):
    return 'NAME:{}, UUID:{}'.format(self.name, self.uuid)

  @classmethod
  def create(cls, json_text):
    # Text -> JSON Dict
    try:
      d = json.loads(json_text)
    except:
      raise Exception('JSON parse error.')

    # Key checks
    if 'name' not in d:
      raise Exception('key "name" not in JSON.')
    if 'external_ip' not in d:
      raise Exception('key "external_ip" not in JSON.')
    if 'netmask' not in d:
      raise Exception('key "netmask" not in JSON.')
    if 'gateway' not in d:
      raise Exception('key "gateway" not in JSON.')
    if 'ntp_server' not in d:
      raise Exception('key "ntp_server" not in JSON.')
    if 'name_server' not in d:
      raise Exception('key "name_server" not in JSON.')
    if 'prism_user' not in d:
      raise Exception('key "prism_user" not in JSON.')
    if 'prism_password' not in d:
      raise Exception('key "prism_password" not in JSON.')
    if 'nodes' not in d:
      raise Exception('key "nodes" not in JSON.')
    for node in d['nodes']:
      if 'host_name' not in node:
        raise Exception('key "host_name" not in JSON.')
      if 'position' not in node:
        raise Exception('key "position" not in JSON.')
      if 'ipmi_mac' not in node:
        raise Exception('key "ipmi_mac" not in JSON.')
      if 'ipmi_ip' not in node:
        raise Exception('key "ipmi_ip" not in JSON.')   
      if 'host_ip' not in node:
        raise Exception('key "host_ip" not in JSON.')
      if 'cvm_ip' not in node:
        raise Exception('key "cvm_ip" not in JSON.')
    
    # Create Asset entry
    name = d['name']
    asset_object = Asset.objects.create(name=name, data='')
    
    # Add UUID to JSON
    d['uuid'] = str(asset_object.uuid)
    
    # Update Asset entry
    asset_object.data = json.dumps(d, indent=2)
    asset_object.save()

    return asset_object.data

  @classmethod
  def update(cls, uuid, json_text):
    # Asset
    asset_object = Asset.objects.filter(uuid=uuid)[0]

    # Text -> JSON Dict
    try:
      d = json.loads(json_text)
    except:
      raise Exception('JSON parse error.')

    # Key checks
    if 'name' not in d:
      raise Exception('key "name" not in JSON.')
    if 'external_ip' not in d:
      raise Exception('key "external_ip" not in JSON.')
    if 'netmask' not in d:
      raise Exception('key "netmask" not in JSON.')
    if 'gateway' not in d:
      raise Exception('key "gateway" not in JSON.')
    if 'ntp_server' not in d:
      raise Exception('key "ntp_server" not in JSON.')
    if 'name_server' not in d:
      raise Exception('key "name_server" not in JSON.')
    if 'prism_user' not in d:
      raise Exception('key "prism_user" not in JSON.')
    if 'prism_password' not in d:
      raise Exception('key "prism_password" not in JSON.')
    if 'nodes' not in d:
      raise Exception('key "nodes" not in JSON.')
    for node in d['nodes']:
      if 'host_name' not in node:
        raise Exception('key "host_name" not in JSON.')
      if 'position' not in node:
        raise Exception('key "position" not in JSON.')
      if 'ipmi_mac' not in node:
        raise Exception('key "ipmi_mac" not in JSON.')
      if 'ipmi_ip' not in node:
        raise Exception('key "ipmi_ip" not in JSON.')   
      if 'host_ip' not in node:
        raise Exception('key "host_ip" not in JSON.')
      if 'cvm_ip' not in node:
        raise Exception('key "cvm_ip" not in JSON.')
    
    # Create Asset entry
    d['uuid'] = str(asset_object.uuid)
    asset_object.name = d['name']
    asset_object.data = json.dumps(d, indent=2)
    asset_object.save()

    return asset_object.data