#!/usr/bin/env bash 

# get password
printf "password: "
read password

# start django
{
  cd django
  source venv/bin/activate
  python manage.py runserver
} &
pid_django=$!

# start node(vue)
{ 
  cd vue
  npm start
} &
pid_node=$!

# start proxy with password
{
  echo "$password" | sudo -S python3 proxy.py
} &
pid_proxy=$!

ctrc()
{
  # kill proxy
  {
    pid_port80=`echo "$password" | sudo -S lsof -ti tcp:80`
    echo "$password" | sudo -S kill -9 $pid_port80
  } &

  # kill node(vue)
  {
    kill -9 $(lsof -ti tcp:8000)
  } &

  # kill django
  {
    kill -9 $(lsof -ti tcp:8080)
  } &

  wait
  exit 0
}

trap ctrc SIGINT
while : ; do : ; done