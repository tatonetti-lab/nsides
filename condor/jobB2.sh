tar xvfz data.tgz

python mlp_shallow_osg.py --suffix 1 | tee mlp_shallow_1.log

tar cvfz shallow_out_1.tgz data scores*.npy *.log *.py model*.npy model*.mtx
