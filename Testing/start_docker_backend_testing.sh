#!/bin/bash

# VARS #
IS_JOB_RUN="True"
REQUEST_TYPE="GET"
IS_REST_API_CONTAINER="True"
MYSQL_PASSWORD="3kwe3gMfyZR3T@K"
IS_MYSQL_CONTAINER_FOR_DOCKER="True"
MYSQL_USER_NAME="freedb_Din_Golan_Container"

wait_for_db() {
  echo ""
  echo "###############"
  echo "# Wait for DB #"
  echo "###############"
  echo ""

  host="$1"
  port="$2"

  echo "Waiting for $host:$port to become available ..."

  while ! nc -z "$host" "$port"; do
    sleep 1
  done

  echo "$host:$port is now available, continuing with the script ..."
}

check_file_exist () {
  echo ""
  echo "##################################"
  echo "# Check if relevant files exists #"
  echo "##################################"
  echo ""

  if [ ! -f "$1" ];
  then
    echo "$1 - Not Exists ..."
    exit 1
  else
    echo "$1 - Exists ..."
    dos2unix "$1"
  fi
}

wait_for_db "$MYSQL_HOST_NAME" "$MYSQL_GUEST_PORT"

check_file_exist "/DevOps_Experts_Final_Project/Testing/docker_backend_testing.py"

/bin/sh -c "sleep 20 && python /DevOps_Experts_Final_Project/Testing/docker_backend_testing.py -u $MYSQL_USER_NAME -p $MYSQL_PASSWORD -i $IS_JOB_RUN -r $REQUEST_TYPE -s $IS_MYSQL_CONTAINER_FOR_DOCKER -d $IS_REST_API_CONTAINER"