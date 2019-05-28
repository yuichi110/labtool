from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse, reverse_lazy

from asset.models import Asset
from segment.models import Segment

#from uuidfield import UUIDField
import uuid
import json

class Cluster(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  asset = models.OneToOneField(Asset, on_delete=models.CASCADE, editable=False)
  segment = models.ForeignKey(Segment, on_delete=models.CASCADE)
  #status = models.TextField()

  def __str__(self):
    return 'Asset:{}, Segment:{}, UUID:{}'.format(self.asset.name, self.segment.name, self.uuid)

  def data(self):
    asset_dict = json.loads(self.asset.data)
    segment_dict = json.loads(self.segment.data)

    if 'alias' in segment_dict:
      asset_nodes = asset_dict['nodes']
      segment_nodes = segment_dict['alias']['nodes']
      n = min(len(asset_nodes), len(segment_nodes))
      new_segment_nodes = []
      for i in range(n):
        segment_nodes[i]['ipmi_mac'] = asset_nodes[i]['ipmi_mac']
        new_segment_nodes.append(segment_nodes[i])
      segment_dict['alias']['nodes'] = new_segment_nodes
      asset_dict = segment_dict['alias']
      del segment_dict['alias']

    cluster_dict = segment_dict
    for (key, value) in asset_dict.items():
      cluster_dict[key] = value
    cluster_dict['uuid'] = str(self.uuid)
    cluster_dict['name'] = self.asset.name
    cluster_dict['asset_uuid'] = str(self.asset.uuid)
    cluster_dict['asset_name'] = self.asset.name
    cluster_dict['segment_uuid'] = str(self.segment.uuid)
    cluster_dict['segment_name'] = self.segment.name
    
    return cluster_dict

  def update_status(self):
    cluster_dict = self.data()
    uuid = cluster_dict['uuid']
    ipmi_macs = []
    host_ips = []
    for node in nodes:
      ipmi_macs.append(node['ipmi_mac'])
      host_ips.append(node['host_ip'])

    fvm_user = ''
    fvm_password = ''
    fvm_ip = ''

    prism_user = cluster_dict['prism_user']
    prism_password = cluster_dict['prism_password']
    prism_ip = cluster_dict['external_ip']

    # check status
