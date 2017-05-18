# Submission of condor jobs to Open Science Grid

The scripts in this folder accomplish the following workflow:

1. Obtains the data from the OSG Stash using HTTP. `get_data.py`
2. Prepares the drug outcome data for input to the model generator.
  * `prepare_data.py` aggregates all reports and outcomes, used for testing model
  * `prepare_data_separate_reports.py` separates reports into positive and negative outcomes, used for training model
3. Run the models.  The output should be each report and the model score.
  * `mlp_dnn.py` runs the deep neural network multilayer perceptron
  * `mlp_otherClf.py` uses TensorFlow to run Logistic Regression and scikit-learn to run AdaBoost, RandomForest and Logistic Regression
4. Evaluate the model by calculating propensity score adjusted proportional reporting ratios (PRRs) for each reaction. Output matrix should have dimensions (reactions x  number of models+non-adjusted PRR). `eval_model.py`

The script to run the job is `nsides_cpu_run1.sh` which contains the workflow described above.  The script also installs the following python packages: `h5py5`, `keras`. The job is submitted to condor via `nsides_cpu_run1.submit` or `nsides_gpu_run1.submit` depending if GPU resources are intended to be used.

An example local workflow on OSG follows:
1. `git clone http://github.com/tatonett-lab/nsides nsides`
2. `cd nsides`
3. Start tensorflow singularity shell: `singularity shell docker://tensorflow/tensorflow:latest`
4. Install dependencies:
 * `/usr/local/bin/pip install --user h5py`
 * `/usr/local/bin/pip install --user keras`
 * `/usr/local/bin/pip install --user wget`
3. `python get_data.py`
4. `python prepare_data.py --model-num 0`
5. `python prepare_data_separate_reports.py --model-num 0`
6. `python mlp_dnn.py --run-on-cpu --model-number 0 > mlp_dnn.out`
7. `source find_good_models.sh`
8. `python mlp_shallow.py --run-comparisons --run-on-cpu --model-number 0`
