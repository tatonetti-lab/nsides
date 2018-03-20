#!/bin/bash

mkdir $1
cd $1

tar xvfz ../nsides_scripts.tgz

mv ../dnn_out_$1_*.tgz .

ls dnn_out_$1_*.tgz | xargs -i tar xvfz {}

if [ $3 == 'IN' ]
then
    python eval_model.py --model-type dnn --model-number $1 --ingredient-level | tee eval_model_dnn.log
else
    python eval_model.py --model-type dnn --model-number $1 | tee eval_model_dnn.log
fi

tar cvfz ../results_$1_dnn.tgz results*.pkl eval_model_dnn.log

rm results*.pkl
rm model*.npy
rm score*.npy

ls -lrth

exit 0
