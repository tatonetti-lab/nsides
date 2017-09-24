#!/bin/bash

MODELIDX=$1
RETRY=$2

cd $MODELIDX

dnn_files=$(ls -m dnn_out_$1_*.tgz)

dnn_files_edit=$(echo "$dnn_files" | sed 's/[]\/$*.^|[]/\\&/g' | tr -d '\n')

echo $dnn_files_edit

sed "s/DNN_FILES_TO_TRANSFER/$dnn_files_edit/g" ../eval_model_dnn.submit.template > eval_model_dnn.submit

MEM="2GB"

if [ "$RETRY" -gt "1" ]; then
    MEM="4GB"
fi

sed -i "s/REDEFINE_MEMORY/$MEM/g" eval_model_dnn.submit
