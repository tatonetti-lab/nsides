tar xvfz data.tgz

/usr/local/bin/pip install --user h5py
/usr/local/bin/pip install --user keras

python mlp_dnn_streaming.py --suffix 2 | tee mlp_dnn_2.log

tar cvfz dnn_out_2.tgz data scores*.npy *.log *.py model*.npy model*.mtx
