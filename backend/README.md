# Submission of condor jobs to Open Science Grid

## How to submit sample job

Make the submission tarball and submit sample DNN job:
1. `mkdir data; cd data`
2. `python ../get_data.py`
3. `cd ..`
4. `source makeworkdir.sh`
5. `cd workdir`
6. `condor_submit_dag workflow_dnn_IN.dag.template`

Submit sample LRC job instead:
4. `source makeworkdir_lrc.sh`
5. `cd workdir_lrc`
6. `condor_submit_dag workflow_lrc_IN.dag.template`

## Script Summary
The scripts in this folder accomplish the following workflow:

1. Obtains the data from the OSG Stash using HTTP. `get_data.py`
2. Prepares the drug outcome data for input to the model generator.
  * `prepare_data_osg.py` aggregates all reports and outcomes, used for forming model
3. Run the models.  The output should be each report and the model score.
  * `mlp_dnn_streaming.py` runs the deep neural network multilayer perceptron
  * `mlp_shallow_osg_lrc.py` runs logistic regression via scikit-learn
4. Evaluate a given model model (DNN, logistic regression) by calculating propensity score adjusted proportional reporting ratios (PRRs) for each reaction. `eval_model.py`
