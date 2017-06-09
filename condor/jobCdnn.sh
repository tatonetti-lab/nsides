tar xvfz dnn_out_*.tgz

python eval_model.py --model-type dnn --model-number $1 | tee eval_model_dnn.log

tar cvfz results_$1_dnn.tgz results*.pkl *.log

