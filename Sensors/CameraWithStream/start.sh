#!/bin/bash

DIR=`dirname $0`
cd $DIR
# ---------Attention----------------
# If you rename the main python file of the operator, update the content of the entry-file-name accordingly

FILE_NAME=`cat entry-file-name`
#-----------------------------------

nohup python3 "${DIR}/${FILE_NAME}" > start.out &

# output PID of last job running in background

echo $! > pid.txt

