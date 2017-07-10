tar xvfz nsides_scripts_lrc.tgz

ls shallow_out_$1_*.tgz | xargs -i tar xvfz {}

python eval_model.py --model-type $2 --model-number $1 | tee eval_model_$2.log

tar cvfz results_$1_$2.tgz results*.pkl *.log
