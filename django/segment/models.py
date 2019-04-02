from django.db import models
from django.core.exceptions import ValidationError

import uuid
import json

class Segment(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100, unique=True)
  data = models.TextField()
  allow_dup_use = models.BooleanField(default=True)

  def __str__(self):
    return 'NAME:{}, UUID:{}'.format(self.name, self.uuid)

  @classmethod
  def create(cls, json_text):

    d = json.loads(json_text)

    if 'name' not in d:
      raise Exception('key "name" not in JSON.')
    if 'foundation_vms' not in d:
      raise Exception('key "foundation_vms" not in JSON.')
    if 'basics' not in d:
      raise Exception('key "basics" not in JSON.')
    if 'containers' not in d:
      raise Exception('key "containers" not in JSON.')
    if 'networks' not in d:
      raise Exception('key "networks" not in JSON.')
    if 'images' not in d:
      raise Exception('key "images" not in JSON.')

    if 'alias' in d:
      ad = d['alias']
      if 'external_ip' not in ad:
        raise Exception('key "external_ip" not in JSON.')
      if 'netmask' not in ad:
        raise Exception('key "netmask" not in JSON.')
      if 'gateway' not in ad:
        raise Exception('key "gateway" not in JSON.')
      if 'ntp_server' not in ad:
        raise Exception('key "ntp_server" not in JSON.')
      if 'name_server' not in ad:
        raise Exception('key "name_server" not in JSON.')
      if 'prism_user' not in ad:
        raise Exception('key "prism_user" not in JSON.')
      if 'prism_password' not in ad:
        raise Exception('key "prism_password" not in JSON.')
      if 'nodes' not in ad:
        raise Exception('key "nodes" not in JSON.')
      for node in ad['nodes']:
        if 'host_name' not in node:
          raise Exception('key "host_name" not in JSON.')
        if 'position' not in node:
          raise Exception('key "position" not in JSON.')
        if 'ipmi_ip' not in node:
          raise Exception('key "ipmi_ip" not in JSON.')   
        if 'host_ip' not in node:
          raise Exception('key "host_ip" not in JSON.')
        if 'cvm_ip' not in node:
          raise Exception('key "cvm_ip" not in JSON.')
    
    name = d['name']
    segment_object = Segment.objects.create(name=name, data='')
    d['uuid'] = str(segment_object.uuid)
    segment_object.data = json.dumps(d, indent=2)
    segment_object.save()

    return segment_object.data

  @classmethod
  def update(cls, uuid, json_text):
    
    # get object
    segment_object = Segment.objects.filter(uuid=uuid)[0]

    # get json
    d = json.loads(json_text)

    if 'name' not in d:
      raise Exception('key "name" not in JSON.')
    if 'foundation_vms' not in d:
      raise Exception('key "foundation_vms" not in JSON.')
    if 'basics' not in d:
      raise Exception('key "basics" not in JSON.')
    if 'containers' not in d:
      raise Exception('key "containers" not in JSON.')
    if 'networks' not in d:
      raise Exception('key "networks" not in JSON.')
    if 'images' not in d:
      raise Exception('key "images" not in JSON.')

    if 'alias' in d:
      ad = d['alias']
      if 'external_ip' not in ad:
        raise Exception('key "external_ip" not in JSON.')
      if 'netmask' not in ad:
        raise Exception('key "netmask" not in JSON.')
      if 'gateway' not in ad:
        raise Exception('key "gateway" not in JSON.')
      if 'ntp_server' not in ad:
        raise Exception('key "ntp_server" not in JSON.')
      if 'name_server' not in ad:
        raise Exception('key "name_server" not in JSON.')
      if 'prism_user' not in ad:
        raise Exception('key "prism_user" not in JSON.')
      if 'prism_password' not in ad:
        raise Exception('key "prism_password" not in JSON.')
      if 'nodes' not in ad:
        raise Exception('key "nodes" not in JSON.')
      for node in ad['nodes']:
        if 'host_name' not in node:
          raise Exception('key "host_name" not in JSON.')
        if 'position' not in node:
          raise Exception('key "position" not in JSON.')
        if 'ipmi_ip' not in node:
          raise Exception('key "ipmi_ip" not in JSON.')   
        if 'host_ip' not in node:
          raise Exception('key "host_ip" not in JSON.')
        if 'cvm_ip' not in node:
          raise Exception('key "cvm_ip" not in JSON.')

    d['uuid'] = str(segment_object.uuid)
    segment_object.name = d['name']
    segment_object.data = json.dumps(d, indent=2)
    segment_object.save()

    return segment_object.data