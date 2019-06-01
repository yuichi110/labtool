from django.db import models

import uuid
import json

class Task(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100)
  data = models.TextField()
  is_complete = models.BooleanField(default=False)
  creation_time = models.DateTimeField(auto_now_add=True)
  update_time = models.DateTimeField(auto_now=True)

  def __str__(self):
    return 'Name:{}, UUID:{}'.format(self.name, self.uuid)

  class Meta:
    ordering = ['-creation_time']

  def get_dict(self):
    d = {
      'uuid':str(self.uuid),
      'name':self.name,
      'status':self.data,
      'is_complete':self.is_complete,
      'creation_time':str(self.creation_time).split('.')[0],
      'update_time':str(self.update_time).split('.')[0]
    }
    return d