#!/usr/bin/env bash 

# get password
printf "password: "
read password

# start django
echo
echo "(1) Starting Django(Backend) at port 8000"
echo
{
  cd django
  source venv/bin/activate
  python manage.py runserver
} &
sleep 5;

# start node(vue)
echo
echo "(2) Starting Node(Frontend) at port 8080"
echo
{ 
  cd vue
  npm start
} &
sleep 5;

# start proxy with sudo
echo
echo "(3) Starting Python HTTP Proxy at port 80"
echo
{
  echo "$password" | sudo -S python3 proxy.py
} &

ctrc()
{
  # kill proxy with sudo
  {
    pid_port80=`echo "$password" | sudo -S lsof -ti tcp:80`
    if [ $pid_port80 ]; then
      echo "$password" | sudo -S kill -9 $pid_port80
    fi
  } &

  # kill node(vue)
  {
    pid_port8000=`lsof -ti tcp:8000`
    if [ $pid_port8000 ]; then
      kill -9 $pid_port8000
    fi
  } &

  # kill django
  {
    pid_port8080=`lsof -ti tcp:8080`
    if [ $pid_port8080 ]; then
      kill -9 $pid_port8080
    fi
  } &

  wait
  exit 0
}

trap ctrc SIGINT
while : ; do sleep 1 ; done