tar xvfz data.tgz

/usr/local/bin/pip install --user h5py
/usr/local/bin/pip install --user keras

python mlp_shallow_osg.py --suffix 2 | tee mlp_shallow_2.log

tar cvfz shallow_out_2.tgz data scores*.npy *.log *.py model*.npy model*.mtx
