#!/bin/bash

REALPATH=$(which realpath)
if [ -z $REALPATH ]; then
realpath() {
    [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}
fi
# Set up directories
SCRIPT_PATH=$(realpath $(dirname "$0"))

  
cd $SCRIPT_PATH

daemon_name=read_publish_deltaohm_hd21abe17

while true
do
python $daemon_name.py 
done

