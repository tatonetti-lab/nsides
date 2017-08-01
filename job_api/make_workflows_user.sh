#!/bin/bash

model_type=$1
# echo $model_type

#ignore first parameter = model type
shift

#concatenate input parameters using deliminator(,)
old="$IFS"
IFS=','
model_indices="$*"
# echo "$model_indices"
IFS=$old

if [ "$model_type" == "dnn" ]; then

    touch workflow.dag
    echo JOB B0 dnn.submit >> workflow.dag
    echo JOB C0 eval_model_dnn.submit >> workflow.dag
    echo JOB C4 eval_model_nopsm.submit >> workflow.dag
    echo  >> workflow.dag
    echo PARENT B0 CHILD C0 C4 >> workflow.dag
    echo  >> workflow.dag
    echo RETRY B0 10 >> workflow.dag
    echo RETRY C0 10 >> workflow.dag
    echo RETRY C4 10 >> workflow.dag
    echo  >> workflow.dag

    echo VARS B0 modelidx=\"$model_indices\" >> workflow.dag
    echo VARS C0 modelidx=\"$model_indices\" >> workflow.dag
    echo VARS C4 modelidx=\"$model_indices\" >> workflow.dag

    touch workflow_gpu.dag
    echo JOB B0 dnn_gpu.submit >> workflow_gpu.dag
    echo JOB C0 eval_model_dnn.submit >> workflow_gpu.dag
    echo JOB C4 eval_model_nopsm.submit >> workflow_gpu.dag
    echo  >> workflow_gpu.dag
    echo PARENT B0 CHILD C0 C4 >> workflow_gpu.dag
    echo  >> workflow_gpu.dag
    echo RETRY B0 10 >> workflow_gpu.dag
    echo RETRY C0 10 >> workflow_gpu.dag
    echo RETRY C4 10 >> workflow_gpu.dag
    echo  >> workflow_gpu.dag
    echo VARS B0 modelidx=\"$model_indices\" >> workflow_gpu.dag
    echo VARS C0 modelidx=\"$model_indices\" >> workflow_gpu.dag
    echo VARS C4 modelidx=\"$model_indices\" >> workflow_gpu.dag

elif [ "$model_type" == "lrc" ]; then
    touch workflow_lronly.dag
    echo JOB B0 shallow_lrc.submit >> workflow_lronly.dag
    echo JOB C3 eval_model_lrc_only.submit >> workflow_lronly.dag
    echo  >> workflow_lronly.dag
    echo PARENT B0 CHILD C3 >> workflow_lronly.dag
    echo  >> workflow_lronly.dag
    echo RETRY B0 10 >> workflow_lronly.dag
    echo RETRY C3 10 >> workflow_lronly.dag
    echo  >> workflow_lronly.dag
    echo VARS B0 modelidx=\"$model_indices\" >> workflow_lronly.dag
    echo VARS C3 modelidx=\"$model_indices\" >> workflow_lronly.dag

else
    echo "Your model type is '$model_type'. Please check your model type (dnn or lrc)."
fi
