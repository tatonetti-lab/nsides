#!/bin/bash

set -e

FOLDER="$(python jobtofolder.py $1)"

if [ $3 == 'IN' ]
then
    gfal-copy -v ./results_$1_$2.tgz gsiftp://gftp.t2.ucsd.edu/hadoop/osg/ColumbiaTBI/ramiv/nsides_output_IN_org/$FOLDER/results_$1_$2.tgz
    gfal-sum gsiftp://gftp-1.t2.ucsd.edu:2811/hadoop/osg/ColumbiaTBI/ramiv/nsides_output_IN_org/$FOLDER/results_$1_$2.tgz md5
else
    gfal-copy -v ./results_$1_$2.tgz gsiftp://gftp.t2.ucsd.edu/hadoop/osg/ColumbiaTBI/ramiv/nsides_output_org/$FOLDER/results_$1_$2.tgz
    gfal-sum gsiftp://gftp-1.t2.ucsd.edu:2811/hadoop/osg/ColumbiaTBI/ramiv/nsides_output_org/$FOLDER/results_$1_$2.tgz md5
fi

rm shallow_out_$1_*.tgz
rm results_$1_$2.tgz

exit 0
