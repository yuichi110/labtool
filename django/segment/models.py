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