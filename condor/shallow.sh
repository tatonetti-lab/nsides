tar xvfz nsides_scripts.tgz

python prepare_data_osg.py --model-number $1 | tee prepare_data.log

python mlp_shallow_osg.py --suffix $2 | tee mlp_shallow_$2.log

tar cvfz shallow_out_$1_$2.tgz scores*.npy *.log *.py model*.npy
