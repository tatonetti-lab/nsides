tar xvfz nsides_scripts_lrc.tgz

python prepare_data_osg.py --model-number $1 | tee prepare_data.log

python mlp_shallow_osg_lrc.py --suffix $2 | tee mlp_shallow_lrc_$2.log

tar cvfz shallow_out_$1_$2.tgz scores*.npy *.log *.py model*.npy
