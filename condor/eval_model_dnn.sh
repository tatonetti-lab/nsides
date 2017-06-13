tar xvfz nsides_scripts.tgz

ls dnn_out_$1_*.tgz | xargs -i tar xvfz {}

python eval_model.py --model-type dnn --model-number $1 | tee eval_model_dnn.log

tar cvfz results_$1_dnn.tgz results*.pkl *.log

