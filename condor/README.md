# Submission of condor jobs to Open Science Grid

## How to submit jobs

Make the submission tarball:
1. `mkdir data; cd data`
2. `python ../get_data.py`
3. `cd ..`
4. `source make_nsides_tarball.sh`

To submit a batch of jobs to **CPU** nodes:
`condor_submit nsides_cpu_run1.submit`

To submit a batch of jobs to **GPU** nodes:
`condor_submit nsides_gpu_run1.submit`

## Script Summary
The scripts in this folder accomplish the following workflow:

1. Obtains the data from the OSG Stash using HTTP. `get_data.py`
2. Prepares the drug outcome data for input to the model generator.
  * `prepare_data.py` aggregates all reports and outcomes, used for testing model
  * `prepare_data_separate_reports.py` separates reports into positive and negative outcomes, used for training model
3. Run the models.  The output should be each report and the model score.
  * `mlp_dnn.py` runs the deep neural network multilayer perceptron
  * `mlp_dnn_streaming.py` runs the deep neural network multilayer perceptron with file streaming to reduce memory usage on OSG worker nodes
  * `mlp_shallow.py` runs shallow classifiers including using TensorFlow to run Logistic Regression and scikit-learn to run AdaBoost, RandomForest and Logistic Regression
4. Evaluate a given model model by calculating propensity score adjusted proportional reporting ratios (PRRs) for each reaction. `eval_model.py`

The script to run the job is `nsides_cpu_run1.sh` which contains the workflow described above.  The script also installs the following python packages: `h5py5`, `keras`. The job is submitted to condor via `nsides_cpu_run1.submit` or `nsides_gpu_run1.submit` depending if GPU resources are intended to be used.

## Example Local Workflow

An example local workflow on OSG follows:
1. `git clone http://github.com/tatonett-lab/nsides nsides`
2. `cd nsides`
3. Start tensorflow singularity shell: `singularity shell docker://tensorflow/tensorflow:latest`
4. Install dependencies:
 * `/usr/local/bin/pip install --user h5py`
 * `/usr/local/bin/pip install --user keras`
 * `/usr/local/bin/pip install --user wget`
3. `mkdir data; cd data; python ../get_data.py; cd ..`
4. `python prepare_data.py --model-number 0`
5. `python prepare_data_separate_reports.py --model-number 0`
6. `python mlp_dnn.py --run-on-cpu --model-number 0 > mlp_dnn.out`
7. `python mlp_shallow.py --run-comparisons --run-on-cpu --model-number 0`
8. `python eval_model.py --model-type tflr --model-number 0`
9. `python eval_model.py --model-type bdt --model-number 0`
10. `python eval_model.py --model-type rfc --model-number 0`
11. `python eval_model.py --model-type lrc --model-number 0`
12. `python eval_model.py --model-type dnn --model-number 0`
13. `python eval_model.py --model-type nopsm --model-number 0`

- - -

# Submission of jobs to the Habanero supercomputing cluster

There are two major differences between OSG and Habanero:

1. Habanero uses the SLURM job runner instead of Condor. SLURM has a more self-contained documentation style, and all necessary options for running a batch of jobs can be packaged into a single shell script.

2. SLURM modifies files entirely within the current working directory (instead of in a separate VM). This means you don't have to worry about sending data to or retrieving data from individual VMs, but you have the extra headache of making sure the intermediate and output files of each job are isolated in ways that don't cause issues down the line (e.g., so that when one job finishes you don't accidentally modify or trash files in use by another job).

The implications of these two facts are accounted for in the job runner script. Use it as follows:

`$ sbatch --array=0-150 nsides_habanero_slurm.sh`

This will queue 150 jobs, one corresponding to each of `--model-number` 1 through 150 (as used in the python scripts in this folder). At the end of each batch, the bash script will package the results and send them to `/rigel/fcs/projects/nsides_results/results_N_gpu.tar.gz`, where `N` is the number of the corresponding job.
