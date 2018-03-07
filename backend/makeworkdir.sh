rm -rf workdir
mkdir workdir
cd workdir

cp ../dnn_prescript_IN.sh .
cp ../dnn_postscript_IN.sh .

cp ../dnn_IN.submit.template .
cp ../dnn_IN.sh.template .

cp ../eval_dnn_prescript_IN.sh .
cp ../eval_dnn_postscript_IN.sh .

cp ../eval_model_dnn_IN.submit.template .

cp ../nsides_scripts.tgz .

cp ../workflow_dnn_IN.dag.template .


cp ../eval_model_dnn.sh .

cp ../submit_jobs_IN.py .
