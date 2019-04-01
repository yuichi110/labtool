"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import time
import threading

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_wsgi_application()

'''
class Cron(threading.Thread):
  def run(self):
    while True:
      try:
        time.sleep(5)
        print('hi')
      except:
        pass

cron = Cron()
cron.daemon = True
cron.start()
'''