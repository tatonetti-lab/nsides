tar xvfz data_$1.tgz

python mlp_shallow_osg.py --suffix $2 | tee mlp_shallow_$2.log

tar cvfz shallow_out_$1_$2.tgz data scores*.npy *.log *.py model*.npy
