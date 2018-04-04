#!/bin/bash

SECTION=$1
RETRY=$2
MODELIDX=$3

cd $MODELIDX

cp shallow_lrc_IN.sh.template shallow_lrc_$SECTION.sh
sed -i "1 i\echo RETRY:$RETRY" ./shallow_lrc_$SECTION.sh


MEM="2GB"

if [ "$RETRY" -gt "1" ]; then
    MEM="4GB"
fi

sed "s/REDEFINE_MEMORY/$MEM/g" shallow_lrc_IN.submit.template > shallow_lrc_$SECTION.submit
sed -i "s/REDEFINE_SCRIPT/shallow_lrc_$SECTION.sh/g" shallow_lrc_$SECTION.submit


if [ "$RETRY" -gt "3" ]; then
    sed -i '1 i\exit 0' ./shallow_lrc_$SECTION.sh
    sed -i "1 i\echo RETRY:$RETRY" ./shallow_lrc_$SECTION.sh
    sed -i "1 i\tar cvfz shallow_$3_$1.tgz test" ./shallow_lrc_$SECTION.sh
    sed -i "1 i\touch test" ./shallow_lrc_$SECTION.sh
    #echo "exit 0" >> ./shallow_lrc.sh
fi

