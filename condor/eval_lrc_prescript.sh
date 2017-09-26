#!/bin/bash

MODELIDX=$1
RETRY=$2

cd $MODELIDX

lrc_files=$(ls -m shallow_out_$1_*.tgz)

lrc_files_edit=$(echo "$lrc_files" | sed 's/[]\/$*.^|[]/\\&/g' | tr -d '\n')

echo $lrx_files_edit

sed "s/DNN_FILES_TO_TRANSFER/$dnn_files_edit/g" ../eval_model_dnn.submit.template > eval_model_dnn.submit

MEM="2GB"

if [ "$RETRY" -gt "1" ]; then
    MEM="4GB"
fi

sed -i "s/REDEFINE_MEMORY/$MEM/g" eval_model_dnn.submit
