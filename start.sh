#!/usr/bin/env bash 

# development
# local
# heroku

# get password
printf "password: "
read -s password

# start django
echo
echo "(1) Starting Django(Backend) at port 8000"
echo
{
  cd django
  source venv/bin/activate
  #echo "$password" | sudo python manage.py runserver
  python manage.py runserver
} &
sleep 5;

# start node(vue)
echo
echo "(2) Starting Vue-JS(Node,Frontend) at port 8080"
echo
{ 
  cd vue
  npm run serve
} &
sleep 10;

# start proxy with sudo
echo
echo "(3) Starting Python HTTP Proxy at port 80"
echo
{
  echo "$password" | sudo -S python proxy.py
} &

ctrc()
{
  # kill proxy
  {
    pids_port80=`echo "$password" | sudo -S lsof -ti tcp:80`
    for pid in $pids_port80 ; do
      echo "$password" | sudo -S kill -9 $pid
    done
  } &

  # kill node(vue)
  {
    pids_port8000=`echo "$password" | sudo -S lsof -ti tcp:8000`
    for pid in $pids_port8000 ; do
      echo "$password" | sudo -S kill -9 $pid
    done
  } &

  # kill django
  {
    pids_port8080=`echo "$password" | sudo -S lsof -ti tcp:8080`
    for pid in $pids_port8080 ; do
      echo "$password" | sudo -S kill -9 $pid
    done
  } &

  wait
  exit 0
}

trap ctrc SIGINT
while : ; do sleep 1 ; done