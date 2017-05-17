# Submission of condor jobs to Open Science Grid

The scripts in this folder accomplish the following.

1. Obtains the data from the OSG Stash using HTTP. `get_data.py`
2. Prepares the drug outcome data for input to the model generator.
  * `prepare_data.py` aggregates all reports and outcomes, used for testing model
  * `prepare_data_separate_reports.py` separates reports into positive and negative outcomes, used for training model
3. Run the models.  The output should be each report and the model score.
  * `mlp_dnn.py` runs the deep neural network multilayer perceptron
  * `mlp_otherClf.py` runs logistic regression using TensorFlow, AdaBoost and RandomForest using scikit-learn
4. Evaluate the model by calculating propensity score adjusted proportional reporting ratios (PRRs) for each reaction. Output matrix should have dimensions (reactions x  number of models+non-adjusted PRR).
