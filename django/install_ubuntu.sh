sudo apt-get -y install python3-pip
sudo apt-get -y install ipmitool
sudo apt-get -y install ansible
sudo apt-get -y install sshpass
pip3 install requests paramiko django whitenoise

mkdir ~/.ssh
cd ~/.ssh
ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
sudo su
cp id_rsa* /root/.ssh/
