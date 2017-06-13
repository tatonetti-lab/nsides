export PATH=/usr/local/cuda-8.0/bin:/usr/loca/bin:/usr/bin:/bin
export LD_LIBRARY_PATH=/usr/local/cuda-8.0/lib64
nvidia-smi
nvcc --version

python prepare_data_osg.py --model-number $1 | tee prepare_data.log

#/usr/local/bin/pip install --user h5py
#/usr/local/bin/pip install --user keras

python mlp_dnn_streaming.py --suffix $2 | tee mlp_dnn_$2.log

tar cvfz dnn_out_$1_$2.tgz scores*.npy *.log *.py model*.npy
