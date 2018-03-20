#!/bin/bash

FOLDER="$(python jobtofolder.py $1)"

if [ $3 == 'IN' ]
then
    gfal-copy -f ./results_$1_$2.tgz gsiftp://gftp.t2.ucsd.edu/hadoop/osg/ColumbiaTBI/ramiv/nsides_output_IN_org/$FOLDER/results_$1_$2.tgz > eval_dnn_post_$1_$2_$3.log 2>&1
    #gfal-sum gsiftp://gftp-1.t2.ucsd.edu:2811/hadoop/osg/ColumbiaTBI/ramiv/nsides_output_IN/results_$1_$2.tgz md5
else
    gfal-copy -f ./results_$1_$2.tgz gsiftp://gftp.t2.ucsd.edu/hadoop/osg/ColumbiaTBI/ramiv/nsides_output_org/$FOLDER/results_$1_$2.tgz > eval_dnn_post_$1_$2_$3.log 2>&1
    #gfal-sum gsiftp://gftp-1.t2.ucsd.edu:2811/hadoop/osg/ColumbiaTBI/ramiv/nsides_output/results_$1_$2.tgz md5
fi

rm dnn_out_$1_*.tgz
rm results_$1_$2.tgz
rm scores*.npy

exit 0
