#!/bin/sh

echo "##################################"
echo "# Check if relevant files exists #"
echo "##################################"

check_file_exist () {
  if [ ! -f "$1" ];
  then
    echo "$1 - Not Exists ..."
    exit 1
  else
    echo "$1 - Exists ..."
    dos2unix "$1"
  fi
}

check_file_exist "/DevOps_Experts_Final_Project/REST_API/rest_app.py"

/bin/sh -c "python /DevOps_Experts_Final_Project/REST_API/rest_app.py"
