#!/bin/bash

# VARS #
IS_JOB_RUN="True"
REQUEST_TYPE="GET"
MYSQL_PASSWORD="keeBetw3%kG4k3R"
MYSQL_USER_NAME="freedb_Din_Golan_Container"

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

check_file_exist "/DevOps_Experts_Final_Project/Testing/docker_backend_testing.py"

/bin/sh -c "sleep 3 && python /DevOps_Experts_Final_Project/Testing/docker_backend_testing.py -u ${MYSQL_USER_NAME} -p ${MYSQL_PASSWORD} -i ${IS_JOB_RUN} -r ${REQUEST_TYPE}"