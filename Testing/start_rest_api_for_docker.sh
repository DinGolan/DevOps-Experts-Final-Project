#!/bin/bash

# VARS #
MYSQL_GUEST_PORT=3306
IS_MYSQL_CONTAINER="True"
MYSQL_HOST_NAME="database"

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

#########################
# Local DB (For Docker) #
#########################
wait_for_db "$MYSQL_HOST_NAME" "$MYSQL_GUEST_PORT"

check_file_exist "/DevOps_Experts_Final_Project/REST_API/rest_app.py"
check_file_exist "/DevOps_Experts_Final_Project/DB/db_pre_definitions.py"

/bin/sh -c "python /DevOps_Experts_Final_Project/DB/db_pre_definitions.py -s $IS_MYSQL_CONTAINER && sleep 5 && python /DevOps_Experts_Final_Project/REST_API/rest_app.py"
