#!/bin/bash

tar xvfz nsides_scripts.tgz

/usr/local/bin/pip install --user h5py
/usr/local/bin/pip install --user keras

# Run the scripts
python prepare_data_osg.py --model-number $1 | tee prepare_data.log
python prepare_data_separate_reports.py --model-number $1 | tee prepare_data_separate_reports.log
python mlp_dnn_streaming.py --run-on-cpu --model-number $1 | tee mlp_dnn.log
python mlp_shallow_osg.py --model-number $1 | tee mlp_shallow_osg.log
python eval_model.py --model-type bdt --model-number $1 | tee eval_model_bdt.log
python eval_model.py --model-type rfc --model-number $1 | tee eval_model_rfc.log
python eval_model.py --model-type lrc --model-number $1 | tee eval_model_lrc.log
python eval_model.py --model-type dnn --model-number $1 | tee eval_model_dnn.log
python eval_model.py --model-type nopsm --model-number $1 | tee eval_model_nopsm.log

# Clean up the data on the remote machine 
rm -rf *.npy
tar cvfz nsides_results_$1.tgz results*.pkl *.log
