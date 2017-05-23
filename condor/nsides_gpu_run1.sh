#!/bin/bash

tar xvfz nsides_scripts.tgz

set -e

export PATH=/usr/local/cuda-8.0/bin:/usr/loca/bin:/usr/bin:/bin
export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64

echo
nvidia-smi
echo

echo
nvcc --version 
echo


/usr/local/bin/pip install --user h5py
/usr/local/bin/pip install --user keras

# Run the scripts
python prepare_data.py --model-number $1 | tee prepare_data.log
python prepare_data_separate_reports.py --model-number $1 | tee prepare_data_separate_reports.log
python mlp_dnn.py --model-number $1 | tee mlp_dnn.log
python mlp_shallow.py --run-comparisons --model-number $1 | tee mlp_shallow.log
python eval_model.py --model-type tflr --model-number $1 | tee eval_model_tflr.log
python eval_model.py --model-type bdt --model-number $1 | tee eval_model_bdt.log
python eval_model.py --model-type rfc --model-number $1 | tee eval_model_rfc.log
python eval_model.py --model-type lrc --model-number $1 | tee eval_model_lrc.log
python eval_model.py --model-type dnn --model-number $1 | tee eval_model_dnn.log
python eval_model.py --model-type nopsm --model-number $1 | tee eval_model_nopsm.log

# Clean up the data on the remote machine 
rm -rf *.npy
tar cvfz nsides_results_$1.tgz results*.pkl *.log
