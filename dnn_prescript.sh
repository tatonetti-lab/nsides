#!/bin/bash

SECTION=$1
RETRY=$2
MODELIDX=$3

cd $MODELIDX
cp ../dnn.sh.template .
cp ../dnn.submit.template .

cp dnn.sh.template dnn_$SECTION.sh
sed -i "1 i\echo RETRY:$RETRY" ./dnn_$SECTION.sh


MEM="2GB"

if [ "$RETRY" -gt "1" ]; then
    MEM="4GB"
fi

sed "s/REDEFINE_MEMORY/$MEM/g" dnn.submit.template > dnn_$SECTION.submit
sed -i "s/REDEFINE_SCRIPT/dnn_$SECTION.sh/g" dnn_$SECTION.submit


if [ "$RETRY" -gt "3" ]; then
    sed -i '1 i\exit 0' ./dnn_$SECTION.sh
    sed -i "1 i\echo RETRY:$RETRY" ./dnn_$SECTION.sh
    #echo "exit 0" >> ./dnn.sh
fi

