#!/bin/sh
#
# Job runner for NSIDES
#
# see github.com/tatonetti-lab/nsides.git
#
#SBATCH --account=fcs
#SBATCH --job-name=NSIDES		 # a single job name
#SBATCH --gres=gpu:1			 # use GPU for tensorflow/CUDA
#SBATCH -c 1				 # 1 cpu core
#SBATCH -t 0-2:00			 # max time: D-HH:MM
#SBATCH -o nsides_results_%A_%a.out	 # Standard output redirection
#SBATCH -e nsides_results_%A_%a.err	 # Standard error redirection

module load cuda80/toolkit cuda80/blas cudnn/5.1
module load anaconda/2-4.2.0

pip install --user tensorflow-gpu keras h5py

python prepare_data.py --model-number ${SLURM_ARRAY_TASK_ID} | tee prepare_data.log
python prepare_data_separate_reports.py --model-number ${SLURM_ARRAY_TASK_ID} | tee prepare_data_separate_reports.log
python mlp_dnn.py --model-number ${SLURM_ARRAY_TASK_ID} | tee mlp_dnn.log
python mlp_shallow.py --run-comparisons --model-number ${SLURM_ARRAY_TASK_ID} | tee mlp_shallow.py
python eval_model.py --model-type tflr --model-number ${SLURM_ARRAY_TASK_ID} | tee eval_model_tflr.log
python eval_model.py --model-type bdt --model-number ${SLURM_ARRAY_TASK_ID} | tee eval_model_bdt.log
python eval_model.py --model-type rfc --model-number ${SLURM_ARRAY_TASK_ID} | tee eval_model_rfc.log
python eval_model.py --model-type lrc --model-number ${SLURM_ARRAY_TASK_ID} | tee eval_model_lrc.log
python eval_model.py --model-type dnn --model-number ${SLURM_ARRAY_TASK_ID} | tee eval_model_dnn.log
python eval_model.py --model-type nopsm --model-number ${SLURM_ARRAY_TASK_ID} | tee eval_model_nopsm.log

rm -rf *.npy
tar -czvf nsides_results_$1.tgz results*.pkl *.log
