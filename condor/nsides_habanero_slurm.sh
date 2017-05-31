#!/bin/sh
#
# Job runner for NSIDES
#
# see github.com/tatonetti-lab/nsides.git
#
#SBATCH --account=fcs
#SBATCH --job-name=NSIDES_%A_%a		 # a single job name
#SBATCH --gres=gpu:1			 # use GPU for tensorflow/CUDA
#SBATCH -c 1				 # 1 cpu core
#SBATCH -t 0-12:00			 # max time: D-HH:MM
#SBATCH -o nsides_results_%A_%a.out	 # Standard output redirection
#SBATCH -e nsides_results_%A_%a.err	 # Standard error redirection

# RUNNING A JOB QUEUE: sbatch --array=0-5 nsides_habanero_slurm.sh

start=`date +%s`

module load cuda80/toolkit cuda80/blas cudnn/5.1
module load anaconda/2-4.2.0

pip install --user tensorflow-gpu keras h5py

i=${SLURM_ARRAY_TASK_ID}

# Move into subdirectory
mkdir $i
cd $i

# Note: Data files are not checked into git, and are located in `data/`, relative to the working directory
python ../prepare_data.py --model-number $i | tee prepare_data.log
python ../prepare_data_separate_reports.py --model-number $i | tee prepare_data_separate_reports.log

# Run the model
python ../mlp_dnn.py --model-number $i | tee mlp_dnn.log
python ../mlp_shallow.py --run-comparisons --model-number $i | tee mlp_shallow.log

# Evaluate the model's performance
python ../eval_model.py --model-type tflr --model-number $i | tee eval_model_tflr.log
python ../eval_model.py --model-type bdt --model-number $i | tee eval_model_bdt.log
python ../eval_model.py --model-type rfc --model-number $i | tee eval_model_rfc.log
python ../eval_model.py --model-type lrc --model-number $i | tee eval_model_lrc.log
python ../eval_model.py --model-type dnn --model-number $i | tee eval_model_dnn.log
python ../eval_model.py --model-type nopsm --model-number $i | tee eval_model_nopsm.log

# Clean up
printf -v j "%03d" $i
tar -czvf ../../../nsides_results/results_"$j"_gpu.tar.gz results*.pkl *.log

cd ..
rm -rf $i

end=`date +%s`

runtime=$((end-start))

echo Elapsed time for running model $i : $runtime
