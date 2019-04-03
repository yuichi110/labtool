import threading
import time

from task.models import Task
from nutanix_foundation import FoundationOps

class FoundationTask(threading.Thread):
  def __init__(self, task_uuid, cluster_dict, aos_image, hypervisor_type, hypervisor_image):
    threading.Thread.__init__(self)
    tasks = Task.objects.filter(uuid=task_uuid)
    if len(tasks) > 0:
      self.task = tasks[0]
    else:
      raise Exception('no task uuid')
    self.task_uuid = task_uuid
    self.cluster_dict = cluster_dict
    self.aos_image = aos_image
    self.hypervisor_type = hypervisor_type
    self.hypervisor_image = hypervisor_image

  def run(self):
    try:
      fo = FoundationOps()
      fo.foundation(self.cluster_dict, self.aos_image)
      fo.eula(self.cluster_dict)
      fo.setup(self.cluster_dict)
    except:
      pass

    self.task.is_complete = True