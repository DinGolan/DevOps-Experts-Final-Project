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

check_file_exist "../REST_API/rest_app.py"

/bin/sh -c "python ../REST_API/rest_app.py && sleep 3"
