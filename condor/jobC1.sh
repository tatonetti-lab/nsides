tar xvfz shallow_out_1.tgz
tar xvfz shallow_out_2.tgz

python eval_model.py --model-type bdt --model-number $1 | tee eval_model_bdt.log
python eval_model.py --model-type rfc --model-number $1 | tee eval_model_rfc.log
python eval_model.py --model-type lrc --model-number $1 | tee eval_model_lrc.log

tar cvfz results_shallow.tgz results*.pkl *.log
