from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse, reverse_lazy

class Cluster(models.Model):
  name = models.CharField(max_length=100)
  user = models.CharField(max_length=100)
  password = models.CharField(max_length=100)

  def __str__(self):
    return self.name

'''
class Cluster(models.Model):
  ipAddress = models.CharField(max_length=100, verbose_name='IP Address')
  userName = models.CharField(max_length=100, verbose_name='User Name')
  password = models.CharField(max_length=100, verbose_name='Password')

class ClusterStatus(models.Model):
  ip_reachability = models.CharField(max_length=100, verbose_name='IP Reachability')
  aos_version = models.CharField(max_length=100, verbose_name='AOS Version')
  ncc_version = models.CharField(max_length=100, verbose_name='NCC Version')
  hypervisor = models.CharField(max_length=100, verbose_name='Hypervisor')
  cluster = models.OneToOneField(Cluster)

class RackableUnit(models.Model):
  modelName = models.CharField(max_length=100, verbose_name='Model Name')
  serial_number = models.CharField(max_length=100, verbose_name='Serial Number')
  number_of_nodes = models.CharField(max_length=100, verbose_name='Number of nodes')
  clusterStatus = models.ForeignKey(ClusterStatus)

class Container(models.Model):
  name = models.CharField(max_length=100, verbose_name='Name')
  uuid = models.CharField(max_length=100, verbose_name='UUID')
  storagePool = models.CharField(max_length=100, verbose_name='StoragePoolUUID')
  cluster = models.ForeignKey(Cluster)

class Network(models.Model):
  name = models.CharField(max_length=100, verbose_name='Name')
  uuid = models.CharField(max_length=100, verbose_name='UUID') 
  nameServer = models.CharField(max_length=100, verbose_name='Name Server') 
  networkAddress = models.CharField(max_length=100, verbose_name='Network Address')
  prefix = models.CharField(max_length=100, verbose_name='Prefix')
  defaultGateway = models.CharField(max_length=100, verbose_name='Default Gateway')
  poolFrom = models.CharField(max_length=100, verbose_name='DHCP Start Address')
  poolTo = models.CharField(max_length=100, verbose_name='DHCP End Address')
  cluster = models.ForeignKey(Cluster)

class Image(models.Model):
  name = models.CharField(max_length=100, verbose_name='Name')
  uuid = models.CharField(max_length=100, verbose_name='UUID')
  url = models.CharField(max_length=100, verbose_name='URL')
  imageType = models.CharField(max_length=100, verbose_name='Image Type')
  container = models.ForeignKey(Container)
  cluster = models.ForeignKey(Cluster)
'''

