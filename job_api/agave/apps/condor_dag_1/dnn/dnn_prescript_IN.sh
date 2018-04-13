#!/bin/bash

SECTION=$1
RETRY=$2
MODELIDX=$3

cp dnn_IN.sh.template dnn_${MODELIDX}_${SECTION}.sh
sed -i "1 i\echo RETRY:$RETRY" ./dnn_${MODELIDX}_${SECTION}.sh


MEM="2GB"

if [ "$RETRY" -gt "1" ]; then
    MEM="4GB"
fi

sed "s/REDEFINE_MEMORY/$MEM/g" dnn_IN.submit.template > dnn_${MODELIDX}_${SECTION}.submit
sed -i "s/REDEFINE_SCRIPT/dnn_${MODELIDX}_${SECTION}.sh/g" dnn_${MODELIDX}_${SECTION}.submit


if [ "$RETRY" -gt "3" ]; then
    sed -i '1 i\exit 0' ./dnn_${MODELIDX}_${SECTION}.sh
    sed -i "1 i\echo RETRY:$RETRY" ./dnn_${MODELIDX}_${SECTION}.sh
    sed -i "1 i\tar cvfz dnn_$3_$1.tgz test" ./dnn_${MODELIDX}_${SECTION}.sh
    sed -i "1 i\touch test" ./dnn_${MODELIDX}_${SECTION}.sh
fi

exit 0
