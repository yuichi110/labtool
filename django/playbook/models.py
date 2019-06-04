from django.db import models
import uuid

# Create your models here.
class Playbook(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100, unique=True)
  body = models.TextField()

  def __str__(self):
    return 'name:{}, uuid:{}'.format(self.name, self.uuid)

  def data(self):
    d = {
      'uuid':str(self.uuid),
      'name':self.name,
      'body':self.body,

      # for django vue select box
      'value':str(self.uuid),
      'text':self.name,
    }
    return d