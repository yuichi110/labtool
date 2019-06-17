#!/usr/bin/env bash 

printf "password: "
read -s password

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
  for pid in $pids_port8000 ; do
    echo "$password" | sudo -S kill -9 $pid
  done
} &

wait
exit 0
