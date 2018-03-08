#!/bin/bash

mkdir $1
cd $1

tar xvfz ../nsides_scripts.tgz

mv ../shallow_out_$1_*.tgz .

ls shallow_out_$1_*.tgz | xargs -i tar xvfz {}

if [ $3 == 'IN' ]
then
    python eval_model.py --model-type nopsm --model-number $1 --ingredient-level | tee eval_model_nopsm.log
    python eval_model.py --model-type $2 --model-number $1 --ingredient-level | tee eval_model_$2.log
else
    python eval_model.py --model-type nopsm --model-number $1 | tee eval_model_nopsm.log
    python eval_model.py --model-type $2 --model-number $1 | tee eval_model_$2.log
fi

tar cvfz ../results_$1_$2.tgz results*.pkl *.log

#if [ $3 == 'IN' ]
#then
#    gfal-copy -v ./results_$1_$2.tgz gsiftp://gftp.t2.ucsd.edu/hadoop/osg/ColumbiaTBI/ramiv/nsides_output_IN/results_$1_$2.tgz
#else
#    gfal-copy -v ./results_$1_$2.tgz gsiftp://gftp.t2.ucsd.edu/hadoop/osg/ColumbiaTBI/ramiv/nsides_output/results_$1_$2.tgz
#fi

#rm results_$1_$2.tgz
rm results*.pkl
rm model*.npy

ls -lrth
