#!/usr/bin/env bash 

printf "password: "
read -s password

{
  pid_port80=`echo "$password" | sudo -S lsof -ti tcp:80`
  echo $pid_port80
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
