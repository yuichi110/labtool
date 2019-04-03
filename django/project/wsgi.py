"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import time
import threading

from django.utils.timezone import get_current_timezone
import datetime

from django.core.wsgi import get_wsgi_application
from task.models import Task

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