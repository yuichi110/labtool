
def test_foundation(cluster_name, aos_image):
  response = requests.get('http://127.0.0.1:8000/api/clusters')
  for cluster in response.json():
    if cluster['name'] != cluster_name:
      continue
    uuid = cluster['uuid']
    d = {
      'aos_image' : aos_image,
      'hypervisor_type' : 'ahv'
    }
    request_body = json.dumps(d, indent=2)
    response = requests.post('http://127.0.0.1:8000/api/operations/foundation/{}'.format(uuid), data=request_body)

def test_start(cluster_name):
  response = requests.get('http://127.0.0.1:8000/api/clusters')
  uuid = ''
  for cluster in response.json():
    if cluster['name'] != cluster_name:
      continue
    uuid = cluster['uuid']

  if uuid == '':
    print('Failed to find the cluster. Abort.')
    exit()

  response = requests.post('http://127.0.0.1:8000/api/operations/start/{}'.format(uuid))

def test_stop(cluster_name):
  response = requests.get('http://127.0.0.1:8000/api/clusters')
  uuid = ''
  for cluster in response.json():
    if cluster['name'] != cluster_name:
      continue
    uuid = cluster['uuid']

  if uuid == '':
    print('Failed to find the cluster. Abort.')
    exit()

  response = requests.post('http://127.0.0.1:8000/api/operations/stop/{}'.format(uuid))


body_httpd = '''---
- name: sample
  hosts: all
  remote_user: root
  
  tasks:

    - name: latest httpd
      yum:
        name: httpd
        state: latest
'''

def create_playbook(name, body):
  d = {
    'name':name,
    'body':body,
  }

  request_body = json.dumps(d, indent=2)
  response = requests.post('http://127.0.0.1:8000/api/playbooks/', request_body)


def test_ansible(playbook_name, hosts, user, password):
  response = requests.get('http://127.0.0.1:8000/api/playbooks/')
  uuid = ''
  for playbook in response.json():
    if playbook['name'] != playbook_name:
      continue
    uuid = playbook['uuid']

  if uuid == '':
    print('Failed to find the cluster. Abort.')
    exit()

  d = {
    'hosts':hosts,
    'user':user,
    'password':password
  }
  request_body = json.dumps(d, indent=2)
  response = requests.post('http://127.0.0.1:8000/api/operations/run_playbook/{}'.format(uuid), request_body)
