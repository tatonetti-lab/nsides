rm -rf workflowdir
mkdir workflowdir

rm -rf workflowdir_gpu
mkdir workflowdir_gpu

cd workflowdir

for i in {0..151}
    do
	touch workflow_$i.dag
        echo JOB B0 dnn.submit >> workflow_$i.dag
#        echo JOB B1 shallow.submit >> workflow_$i.dag
        echo JOB C0 eval_model_dnn.submit >> workflow_$i.dag
#	echo JOB C1 eval_model_bdt.submit >> workflow_$i.dag
#	echo JOB C2 eval_model_rfc.submit >> workflow_$i.dag
#	echo JOB C3 eval_model_lrc.submit >> workflow_$i.dag
	echo JOB C4 eval_model_nopsm.submit >> workflow_$i.dag
        echo  >> workflow_$i.dag
 #       echo PARENT B0 CHILD C0 >> workflow_$i.dag
 #       echo PARENT B1 CHILD C1 C2 C3 C4 >> workflow_$i.dag
	echo PARENT B0 CHILD C0 C4 >> workflow_$i.dag
        echo  >> workflow_$i.dag
        echo RETRY B0 10 >> workflow_$i.dag
#        echo RETRY B1 10 >> workflow_$i.dag
        echo RETRY C0 10 >> workflow_$i.dag
#        echo RETRY C1 10 >> workflow_$i.dag
#	echo RETRY C2 10 >> workflow_$i.dag
#	echo RETRY C3 10 >> workflow_$i.dag
  	echo RETRY C4 10 >> workflow_$i.dag
        echo  >> workflow_$i.dag
        echo VARS B0 modelidx=\"$i\" >> workflow_$i.dag
#        echo VARS B1 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS C0 modelidx=\"$i\" >> workflow_$i.dag
#        echo VARS C1 modelidx=\"$i\" >> workflow_$i.dag
#        echo VARS C2 modelidx=\"$i\" >> workflow_$i.dag
#        echo VARS C3 modelidx=\"$i\" >> workflow_$i.dag
	echo VARS C4 modelidx=\"$i\" >> workflow_$i.dag
    done

cd ..
cd workflowdir_gpu

for i in {0..151}
    do
	touch workflow_$i.dag
        echo JOB B0 dnn_gpu.submit >> workflow_$i.dag
#        echo JOB B1 shallow.submit >> workflow_$i.dag
        echo JOB C0 eval_model_dnn.submit >> workflow_$i.dag
#	echo JOB C1 eval_model_bdt.submit >> workflow_$i.dag
#	echo JOB C2 eval_model_rfc.submit >> workflow_$i.dag
#	echo JOB C3 eval_model_lrc.submit >> workflow_$i.dag
	echo JOB C4 eval_model_nopsm.submit >> workflow_$i.dag
        echo  >> workflow_$i.dag
#        echo PARENT B0 CHILD C0 >> workflow_$i.dag
#        echo PARENT B1 CHILD C1 C2 C3 C4 >> workflow_$i.dag
        echo PARENT B0 CHILD C0 C4 >> workflow_$i.dag
        echo  >> workflow_$i.dag
        echo RETRY B0 10 >> workflow_$i.dag
#        echo RETRY B1 10 >> workflow_$i.dag
        echo RETRY C0 10 >> workflow_$i.dag
#        echo RETRY C1 10 >> workflow_$i.dag
# 	echo RETRY C2 10 >> workflow_$i.dag
#	echo RETRY C3 10 >> workflow_$i.dag
   	echo RETRY C4 10 >> workflow_$i.dag
        echo  >> workflow_$i.dag
        echo VARS B0 modelidx=\"$i\" >> workflow_$i.dag
#        echo VARS B1 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS C0 modelidx=\"$i\" >> workflow_$i.dag
 #       echo VARS C1 modelidx=\"$i\" >> workflow_$i.dag
  #      echo VARS C2 modelidx=\"$i\" >> workflow_$i.dag
   #     echo VARS C3 modelidx=\"$i\" >> workflow_$i.dag
	echo VARS C4 modelidx=\"$i\" >> workflow_$i.dag
    done

cd ..
