import requests
import os
import json

URL_PREFIX = 'http://10.149.245.90:80'

# Change dir to Django root.
#script_dir = os.path.dirname(__file__)
#print('dir: ' + script_dir)
#os.chdir(script_dir)

FILE_ASSET_CONFIG = 'founder_asset.json'
FILE_SEGMENT_CONFIG = 'founder_segment.json'
FILE_CLUSTER_CONFIG = 'founder_cluster.json'

try:
  print('loading asset config.')
  JSON_ASSET_CONFIG = json.loads(open(FILE_ASSET_CONFIG).read())
  print('loading segment config.')
  JSON_SEGMENT_CONFIG = json.loads(open(FILE_SEGMENT_CONFIG).read())
  print('loading cluster config.')
  JSON_CLUSTER_CONFIG = json.loads(open(FILE_CLUSTER_CONFIG).read())
except Exception as e:
  print(e)
  exit()


  JSON_SEGMENT_CONFIG = json.loads(open(FILE_SEGMENT_CONFIG).read())
  JSON_CLUSTER_CONFIG = json.loads(open(FILE_CLUSTER_CONFIG).read())
def delete_all():
  print('delete_all()')
  response = requests.get(URL_PREFIX + '/api/clusters')
  for cluster in response.json():
    uuid = cluster['uuid']
    requests.delete(URL_PREFIX + '/api/clusters/{}'.format(uuid))

  response = requests.get(URL_PREFIX + '/api/segments')
  for cluster in response.json():
    uuid = cluster['uuid']
    requests.delete(URL_PREFIX + '/api/segments/{}'.format(uuid))

  response = requests.get(URL_PREFIX + '/api/assets')
  for cluster in response.json():
    uuid = cluster['uuid']
    requests.delete(URL_PREFIX + '/api/assets/{}'.format(uuid))

def create_assets():
  print('create_assets()')
  asset_uuid_dict = {}
  for asset in JSON_ASSET_CONFIG:
    request_body = json.dumps(asset, indent=2)
    response = requests.post(URL_PREFIX + '/api/assets', data=request_body)
    uuid = response.json()['uuid']
    asset_uuid_dict[asset['name']] = uuid
    print(' - {}'.format(uuid))
  return asset_uuid_dict

def create_segments():
  print('create_assets()')
  segment_uuid_dict = {}
  for segment in JSON_SEGMENT_CONFIG:
    request_body = json.dumps(segment, indent=2)
    response = requests.post(URL_PREFIX + '/api/segments', data=request_body)
    uuid = response.json()['uuid']
    segment_uuid_dict[segment['name']] = uuid
    print(' - {}'.format(uuid))
  return segment_uuid_dict

def create_clusters(asset_dict, segment_dict):
  print('create_clusters()')
  for (asset, segment) in JSON_CLUSTER_CONFIG.items():
    asset_uuid = asset_dict[asset]
    segment_uuid = segment_dict[segment]
    d = {
      'asset':asset_uuid,
      'segment':segment_uuid,
    }
    request_body = json.dumps(d, indent=2)
    response = requests.post(URL_PREFIX + '/api/clusters', data=request_body)
    del asset_dict[asset]

  for (asset_name, asset_uuid) in asset_dict.items():
    d = {
      'asset':asset_uuid,
      'segment':segment_dict['main'],
    }
    request_body = json.dumps(d, indent=2)
    response = requests.post(URL_PREFIX + '/api/clusters', data=request_body)

if __name__ == '__main__':
  delete_all()
  asset_dict = create_assets()
  segment_dict = create_segments()
  create_clusters = create_clusters(asset_dict, segment_dict)

  