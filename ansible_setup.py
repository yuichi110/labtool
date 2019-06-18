import requests
import os
import json

URL_PREFIX = 'http://10.149.245.90:80'
DIR = 'playbooks'

def delete_playbooks():
  print('delete_playbooks()')
  response = requests.get(URL_PREFIX + '/api/playbooks/')
  for playbook in response.json():
    uuid = playbook['uuid']
    name = playbook['name']
    response = requests.delete(URL_PREFIX + '/api/playbooks/{}'.format(uuid))
    result = 'success' if response.ok else 'fail' 
    print('  - {} : {}'.format(name, result))
  print()

def add_playbooks():
  print('add_playbooks()')
  all_files = os.listdir(path=DIR)
  file_files = [os.path.join(DIR, f) for f in all_files if os.path.isfile(os.path.join(DIR, f))]

  for file in file_files:
    name = file.split('/')[-1].split('.')[0]
    fin = open(file, 'r')
    body = fin.read()
    fin.close()

    d = {
      'name':name,
      'body':body,
    }
    request_body = json.dumps(d, indent=2)
    response = requests.post(URL_PREFIX + '/api/playbooks/', request_body)
    result = 'success' if response.ok else 'fail' 
    print('  - {} : {}'.format(name, result))
  print()

if __name__ == '__main__':
  delete_playbooks()
  add_playbooks()
