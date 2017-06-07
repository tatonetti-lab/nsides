tar xvfz dnn_out_1.tgz
tar xvfz dnn_out_2.tgz

python eval_model.py --model-type dnn --model-number $1 | tee eval_model_dnn.log
python eval_model.py --model-type nopsm --model-number $1 | tee eval_model_nospm.log

tar cvfz results_$1_dnn.tgz results*.pkl *.log
