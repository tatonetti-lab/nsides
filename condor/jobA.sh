#!/bin/bash

tar xvfz nsides_scripts.tgz

# Run the scripts
python prepare_data_osg.py --model-number $1 | tee prepare_data.log
rm -rf data
tar cvfz data.tgz model*.mtx model*.npy *.log *.py
