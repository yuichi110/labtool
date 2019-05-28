"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import time
import threading
import random

from django.utils.timezone import get_current_timezone
import datetime

from django.core.wsgi import get_wsgi_application
from task.models import Task

from cluster.models import Cluster
from background_tasks import StatusCheckTask

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Delete old task at beginning of process.
# Mark is_completed if it isn't.
now = datetime.datetime.now(tz=get_current_timezone())
one_day = datetime.timedelta(1)
for task_object in Task.objects.all():
  diff = now - task_object.update_time
  if diff > one_day:
    task_object.delete()
    continue
  if not task_object.is_complete:
    task_object.is_complete = True
    task_object.save()

# Start Server
application = get_wsgi_application()

# Start task clean thread.
class TaskCleaner(threading.Thread):
  def run(self):
    while True:
      try:
        now = datetime.datetime.now(tz=get_current_timezone())
        for task_object in Task.objects.all():
          if not task_object.is_complete:
            continue
          diff = now - task_object.update_time
          if diff > one_day:
            task_object.delete()
        time.sleep(60 * 60)
      except:
        pass
tc = TaskCleaner()
tc.daemon = True
tc.start()

# Start cluster status check thread.
class StatusChecker(threading.Thread):
  def run(self):
    while True:
      try:
        for cluster in Cluster.objects.all():
          sleep = random.randint(1, 60)
          d = cluster.data()
          uuid = d['uuid']
          fvm_ip = d['foundation_vms']['ip_addresses'][0]
          fvm_user = d['foundation_vms']['user']
          fvm_password = d['foundation_vms']['password']
          ipmi_mac_list = []
          host_ips = []
          for node in d['nodes']:
            ipmi_mac_list.append(node['ipmi_mac'])
            host_ips.append(node['host_ip'])
          prism_ip = d['external_ip']
          prism_name = d['prism_user']
          prism_password = d['prism_password']

          sct = StatusCheckTask(uuid, fvm_ip, fvm_user, fvm_password, ipmi_mac_list, host_ips, prism_ip, prism_name, prism_password, sleep)
          sct.daemon = True
          sct.start()

        time.sleep(120)

      except Exception as e:
        print(e)

sc = StatusChecker()
sc.daemon = True
sc.start()