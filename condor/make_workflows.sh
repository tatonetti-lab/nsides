rm -rf workflowdir
mkdir workflowdir
cd workflowdir

if [[ "$1" == "cpu" ]]
then
    for i in {0..149}
    do
	touch workflow_$i.dag
        echo JOB A jobA.submit >> workflow_$i.dag
        echo JOB B0 jobB0.submit >> workflow_$i.dag
        echo JOB B1 jobB1.submit >> workflow_$i.dag
        echo JOB B2 jobB2.submit >> workflow_$i.dag
        echo JOB B3 jobB3.submit >> workflow_$i.dag
        echo JOB C0 jobC0.submit >> workflow_$i.dag
        echo JOB C1 jobC1.submit >> workflow_$i.dag
        echo  >> workflow_$i.dag
        echo PARENT A CHILD B0 B1 B2 B3 >> workflow_$i.dag
        echo PARENT B0 B1 CHILD C0 >> workflow_$i.dag
        echo PARENT B2 B3 CHILD C1 >> workflow_$i.dag
        echo  >> workflow_$i.dag
        echo RETRY B0 5 >> workflow_$i.dag
        echo RETRY B1 1 >> workflow_$i.dag
        echo  >> workflow_$i.dag
        echo VARS A modelidx=\"$i\" >> workflow_$i.dag
        echo VARS B0 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS B1 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS B2 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS B3 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS C0 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS C1 modelidx=\"$i\" >> workflow_$i.dag
    done
fi

if [[ "$1" == "gpu" ]]
then
    for i in {0..149}
    do
	touch workflow_$i.dag
        echo JOB A jobA.submit >> workflow_$i.dag
        echo JOB B0 jobB0_gpu.submit >> workflow_$i.dag
        echo JOB B1 jobB1_gpu.submit >> workflow_$i.dag
        echo JOB B2 jobB2.submit >> workflow_$i.dag
        echo JOB B3 jobB3.submit >> workflow_$i.dag
        echo JOB C0 jobC0.submit >> workflow_$i.dag
        echo JOB C1 jobC1.submit >> workflow_$i.dag
        echo  >> workflow_$i.dag
        echo PARENT A CHILD B0 B1 B2 B3 >> workflow_$i.dag
        echo PARENT B0 B1 CHILD C0 >> workflow_$i.dag
        echo PARENT B2 B3 CHILD C1 >> workflow_$i.dag
        echo  >> workflow_$i.dag
        echo RETRY B0 5 >> workflow_$i.dag
        echo RETRY B1 1 >> workflow_$i.dag
        echo  >> workflow_$i.dag
        echo VARS A modelidx=\"$i\" >> workflow_$i.dag
        echo VARS B0 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS B1 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS B2 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS B3 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS C0 modelidx=\"$i\" >> workflow_$i.dag
        echo VARS C1 modelidx=\"$i\" >> workflow_$i.dag
    done
fi

cd ..
