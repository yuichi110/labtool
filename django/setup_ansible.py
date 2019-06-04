import json

httpd = ('httpd', '''
- name: latest httpd
  yum:
    name: httpd
    state: latest
''')