#!/bin/bash

MODELIDX=$1

cd $MODELIDX

dnn_file=$(ls dnn_out_$1_*.tgz | head -n 1)

dnn_file_edit=$(echo "$dnn_file" | sed 's/[]\/$*.^|[]/\\&/g' | tr -d '\n')

echo $dnn_file_edit

sed "s/DNN_FILE_TO_TRANSFER/$dnn_file_edit/g" ../eval_model_nopsm.submit.template > eval_model_nopsm.submit
