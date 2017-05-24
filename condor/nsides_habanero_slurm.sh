#!/bin/sh
#
# Job runner for NSIDES
#
# see github.com/tatonetti-lab/nsides.git
#
#SBATCH --account=fcs
#SBATCH --job-name=NSIDES
#SBATCH --gres=gpu:1
#SBATCH -c 1
#SBATCH --time=1:00

module load cuda80/toolkit cuda80/blas cudnn/5.1
module load anaconda/2-4.2.0

pip install --user tensorflow-gpu keras h5py

python prepare_data.py --model-number $1 | tee prepare_data.log
python prepare_data_separate_reports.py --model-number $1 | tee prepare_data_separate_reports.log
python mlp_dnn.py --model-number $1 | tee mlp_dnn.log
python mlp_shallow.py --run-comparisons --model-number $1 | tee mlp_shallow.py
python eval_model.py --model-type tflr --model-number $1 | tee eval_model_tflr.log
python eval_model.py --model-type bdt --model-number $1 | tee eval_model_bdt.log
python eval_model.py --model-type rfc --model-number $1 | tee eval_model_rfc.log
python eval_model.py --model-type lrc --model-number $1 | tee eval_model_lrc.log
python eval_model.py --model-type dnn --model-number $1 | tee eval_model_dnn.log
python eval_model.py --model-type nopsm --model-number $1 | tee eval_model_nopsm.log

rm -rf *.npy
tar -czvf nsides_results_$1.tgz results*.pkl *.log
