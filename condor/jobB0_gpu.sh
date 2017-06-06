tar xvfz data.tgz

/usr/local/bin/pip install --user h5py
/usr/local/bin/pip install --user keras

python mlp_dnn_streaming.py --suffix 1 | tee mlp_dnn_1.log

tar cvfz dnn_out_1.tgz data scores*.npy *.log *.py model*.npy model*.mtx
