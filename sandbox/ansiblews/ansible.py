import subprocess

def ssh_copy_id(host, remote_user, password):
  command = 'echo "{}" | sshpass ssh-copy-id {}@{}'.format(password, remote_user, host)
  res_bytes = subprocess.check_output(command, shell=True)
  res_string = res_bytes.decode('utf-8').strip()
  print(res_string)

def ansible_playbook(inventory, playbook):
  command = 'ansible-playbook -i {} {}'.format(inventory, playbook)
  res_bytes = subprocess.check_output(command, shell=True)
  res_string = res_bytes.decode('utf-8').strip()
  print(res_string)

ssh_copy_id('10.149.245.108', 'root', 'nutanix/4u')
ansible_playbook('inventory', 'playbook.yml')
