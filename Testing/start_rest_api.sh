#!/bin/bash

wait_for_db() {
  echo "###############"
  echo "# Wait for DB #"
  echo "###############"

  host="$1"
  port="$2"

  echo "Waiting for $host:$port to become available ..."

  while ! nc -z "$host" "$port"; do
    sleep 1
  done

  echo "$host:$port is now available, continuing with the script ..."
}

check_file_exist () {
  echo "##################################"
  echo "# Check if relevant files exists #"
  echo "##################################"

  if [ ! -f "$1" ];
  then
    echo "$1 - Not Exists ..."
    exit 1
  else
    echo "$1 - Exists ..."
    dos2unix "$1"
  fi
}

wait_for_db "database" "3306"

check_file_exist "/DevOps_Experts_Final_Project/REST_API/rest_app.py"

/bin/sh -c "python /DevOps_Experts_Final_Project/REST_API/rest_app.py"
