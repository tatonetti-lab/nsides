export PATH=/usr/local/cuda-8.0/bin:/usr/loca/bin:/usr/bin:/bin
export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64
nvidia-smi
nvcc --version

tar xvfz data_$1.tgz

/usr/local/bin/pip install --user h5py
/usr/local/bin/pip install --user keras

python mlp_dnn_streaming.py --suffix $2 | tee mlp_dnn_$2.log

tar cvfz dnn_out_$1_$2.tgz data scores*.npy *.log *.py
