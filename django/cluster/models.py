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

  def __str__(self):
    return 'Asset:{}, Segment:{}, UUID:{}'.format(self.asset.name, self.segment.name, self.uuid)

  def data(self):
    return ''
