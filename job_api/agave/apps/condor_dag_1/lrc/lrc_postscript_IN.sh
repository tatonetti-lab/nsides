#!/bin/bash

FOLDER="$(python jobtofolder.py $2)"

gfal-copy -v ./shallow_out_$2_$1.tgz gsiftp://gftp.t2.ucsd.edu/hadoop/osg/ColumbiaTBI/ramiv/nsides_output_IN_org/$FOLDER/shallow_out_$2_$1_IN.tgz
gfal-ls gsiftp://gftp-1.t2.ucsd.edu:2811/hadoop/osg/ColumbiaTBI/ramiv/nsides_output_IN_org/$FOLDER/shallow_out_$2_$1_IN.tgz

#rm shallow_out_$2_$1.tgz

exit 0
