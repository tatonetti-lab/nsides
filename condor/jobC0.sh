tar xvfz dnn_out_1.tgz
tar xvfz dnn_out_2.tgz

python eval_model.py --model-type dnn | tee eval_model_dnn.log
python eval_model.py --model-type nopsm | tee eval_model_nospm.log

tar cvfz results_dnn.tgz results*.pkl *.log
