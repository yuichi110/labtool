#!/usr/bin/env bash 

printf "password: "
read password

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

exit 0
