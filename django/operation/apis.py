from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from cluster.models import Cluster
from playbook.models import Playbook
from task.models import Task

from uuid import UUID
import json

from background_tasks import FoundationTask, ClusterStopTask, ClusterStartTask, AnsibleTask

class OperationApi:

  @classmethod
  def run_playbook(cls, request, uuid):
    if request.method not in ['POST']:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    try:
      playbook = Playbook.objects.get(uuid=uuid)
    except Exception as e:
      response_body = json.dumps({'error':'playbook object not found'}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    try:
      json_text = request.body.decode()
      d = json.loads(json_text)
      hosts = d['hosts']
      user = d['user']
      password = d['password']
    except:
      response_body = json.dumps({'error':"request body has problem"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    playbook_header =  '---\n'
    playbook_header += '- name: ' + playbook.name + '\n'
    playbook_header += '  hosts: all\n'
    playbook_header += '  remote_user: ' + user + '\n'
    playbook_header += '  tasks:\n'

    body_with_indent_list = ['  {}'.format(line) for line in playbook.body.split('\n')]
    playbook_body = '\n'.join(body_with_indent_list)

    playbook_content = playbook_header + playbook_body
    print(playbook_content)

    task = Task.objects.create(name='Run playbook {}'.format(playbook.name), data='')
    ansible_task = AnsibleTask(str(task.uuid), hosts, user, password, playbook_content)
    ansible_task.daemon = True
    ansible_task.start()

    response_body = json.dumps({'uuid':str(task.uuid)}, indent=2)
    return HttpResponse(response_body, content_type='application/json')

  @classmethod
  def start(cls, request, uuid):
    if request.method not in ['POST']:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    try:
      cluster = Cluster.objects.get(uuid=uuid)
    except Exception as e:
      response_body = json.dumps({'error':'cluster object not found'}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    cluster_dict = cluster.data()
    ipmi_ips = []
    host_ips = []
    cvm_ips = []
    for node in cluster_dict['nodes']:
      ipmi_ips.append(node['ipmi_ip'])
      host_ips.append(node['host_ip'])
      cvm_ips.append(node['cvm_ip'])
    prism_ip = cluster_dict['external_ip']
    prism_user = cluster_dict['prism_user']
    prism_password = cluster_dict['prism_password']

    task = Task.objects.create(name='Starting Cluster {}'.format(cluster_dict['name']), data='')
    cluster_start_task = ClusterStartTask(str(task.uuid), ipmi_ips, host_ips, cvm_ips, prism_ip, prism_user, prism_password)
    cluster_start_task.daemon = True
    cluster_start_task.start()

    return HttpResponse('{}', content_type='application/json')


  @classmethod
  def stop(cls, request, uuid):
    if request.method not in ['POST']:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    try:
      cluster = Cluster.objects.get(uuid=uuid)
    except Exception as e:
      response_body = json.dumps({'error':'cluster object not found'}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    cluster_dict = cluster.data()
    prism_ip = cluster_dict['external_ip']
    prism_user = cluster_dict['prism_user']
    prism_password = cluster_dict['prism_password']

    task = Task.objects.create(name='Stopping Cluster {}'.format(cluster_dict['name']), data='')
    cluster_stop_task = ClusterStopTask(str(task.uuid), prism_ip, prism_user, prism_password)
    cluster_stop_task.daemon = True
    cluster_stop_task.start()

    return HttpResponse('{}', content_type='application/json')


  @classmethod
  def foundation(cls, request, uuid):
    if request.method not in ['POST']:
      response_body = json.dumps({'error':"unsupported method : '{}'".format(request.method)}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    try:
      json_text = request.body.decode()
      d = json.loads(json_text)
      aos_image = d['aos_image']
      hypervisor_type = d['hypervisor_type']
      if hypervisor_type != 'ahv':
        hypervisor_image = d['hypervisor_image']
      else:
        hypervisor_image = ''
    except:
      response_body = json.dumps({'error':"request body has problem"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    try:
      UUID(uuid, version=4)
    except:
      response_body = json.dumps({'error':"incorrect uuid format"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    if hypervisor_type not in ['ahv', 'esx', 'hyperv']:
      response_body = json.dumps({'error':"unsupported hypervisor type"}, indent=2)
      return HttpResponseBadRequest(response_body, content_type='application/json')

    try:
      cluster = Cluster.objects.get(uuid=uuid)
    except:
      response_body = json.dumps({'error':'cluster object not found'}, indent=2)
      return HttpResponseNotFound(response_body, content_type='application/json')

    cluster_dict = cluster.data()
    task = Task.objects.create(name='Foundation {}'.format(cluster_dict['name']), data='{}')
    try:
      ftask = FoundationTask(str(task.uuid), cluster_dict,
       aos_image, hypervisor_type, hypervisor_image)
      ftask.daemon = True
    except:
      task.is_complete = True
      task.save()
      
    ftask.start()

    return HttpResponse('{}', content_type='application/json')