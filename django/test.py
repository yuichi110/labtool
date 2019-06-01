import requests
import os
import json

def test_asset_segment_cluster():
  # Delete all
  print('Deleting clusters, segments, assets')
  response = requests.get('http://127.0.0.1:8000/api/clusters')
  for cluster in response.json():
    uuid = cluster['uuid']
    requests.delete('http://127.0.0.1:8000/api/clusters/{}'.format(uuid))

  response = requests.get('http://127.0.0.1:8000/api/segments')
  for cluster in response.json():
    uuid = cluster['uuid']
    requests.delete('http://127.0.0.1:8000/api/segments/{}'.format(uuid))

  response = requests.get('http://127.0.0.1:8000/api/assets')
  for cluster in response.json():
    uuid = cluster['uuid']
    requests.delete('http://127.0.0.1:8000/api/assets/{}'.format(uuid))

  CONFIG_FILE = 'foundation_config.json'
  dir_path = os.path.dirname(__file__)
  if dir_path == '':
    config_path = CONFIG_FILE
  else:
    config_path = '{}/{}'.format(dir_path, CONFIG_FILE)
  config = json.loads(open(config_path).read())

  # Create Asset
  print('Creating assets')
  asset_uuid_dict = {}
  for asset in config['assets']:
    request_body = json.dumps(asset, indent=2)
    response = requests.post('http://127.0.0.1:8000/api/assets', data=request_body)
    uuid = response.json()['uuid']
    asset_uuid_dict[asset['name']] = uuid
    print(' - {}'.format(uuid))

  print('Creating segments')
  segment_uuid_dict = {}
  for segment in config['segments']:
    request_body = json.dumps(segment, indent=2)
    response = requests.post('http://127.0.0.1:8000/api/segments', data=request_body)
    uuid = response.json()['uuid']
    segment_uuid_dict[segment['name']] = uuid
    print(' - {}'.format(uuid))

  print('Creating clusters')
  for (asset_name, asset_uuid) in asset_uuid_dict.items():
    if asset_name == 'poc09':
      d = {
        'asset':asset_uuid,
        'segment':segment_uuid_dict['training01']
      }
    elif asset_name == 'poc10':
      d = {
        'asset':asset_uuid,
        'segment':segment_uuid_dict['training02']
      }
    else:
      d = {
        'asset':asset_uuid,
        'segment':segment_uuid_dict['main']
      }
    request_body = json.dumps(d, indent=2)
    response = requests.post('http://127.0.0.1:8000/api/clusters', data=request_body)
    uuid = response.json()['uuid']
    print(' - {}'.format(uuid))

  print('Deleting clusters, segments, assets')
  response = requests.get('http://127.0.0.1:8000/api/clusters')
  for cluster in response.json():
    print('----')
    print(json.dumps(cluster, indent=2))
    

def test_foundation(cluster_name, aos_image):
  response = requests.get('http://127.0.0.1:8000/api/clusters')
  for cluster in response.json():
    if cluster['name'] != cluster_name:
      continue
    uuid = cluster['uuid']
    d = {
      'cluster_uuid' : uuid,
      'aos_image' : aos_image,
      'hypervisor_type' : 'ahv'
    }
    request_body = json.dumps(d, indent=2)
    response = requests.post('http://127.0.0.1:8000/api/operations/foundation', data=request_body)

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

if __name__ == '__main__':
  #test_foundation('poc10', 'nutanix_installer_package-release-euphrates-5.5.7-stable.tar')
  #test_start('poc10')
  test_stop('poc10')
  