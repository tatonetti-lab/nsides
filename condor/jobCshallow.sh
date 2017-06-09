tar xvfz shallow_out_*.tgz

python eval_model.py --model-type $2 --model-number $1 | tee eval_model_bdt.log

tar cvfz results_$1_$2.tgz results*.pkl *.log
