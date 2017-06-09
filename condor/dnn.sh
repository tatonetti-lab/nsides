tar xvfz data_$1.tgz

/usr/local/bin/pip install --user h5py
/usr/local/bin/pip install --user keras

python mlp_dnn_streaming.py --run-on-cpu --suffix $2 | tee mlp_dnn_$2.log

tar cvfz dnn_out_$1_$2.tgz data scores*.npy *.log *.py model*.npy
