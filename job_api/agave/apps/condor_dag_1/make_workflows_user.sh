#!/bin/bash

model_indices=${model_indexes}
# model_indices=$1

if [ -z "${model_indices}" ]; then
    agave_log_response "Model index is not specified."
    exit 1;
fi

# generate dnn workflow
DNN_DAG_FILE='workflow_dnn_IN.dag'
DNN_FILENAME='dnn/workflow_dnn_IN.dag'
if [ -f ${DNN_FILENAME} ]; then
    rm ${DNN_FILENAME}
fi

touch ${DNN_FILENAME}
for i in {0..19}
do
    echo JOB B${i} dnn_${model_indices}_${i}.submit >> ${DNN_FILENAME}
    echo SCRIPT PRE B${i} dnn_prescript_IN.sh $i \$RETRY ${model_indices} >> ${DNN_FILENAME}
    echo SCRIPT POST B${i} dnn_postscript_IN.sh $i ${model_indices} >> ${DNN_FILENAME}
    echo RETRY B${i} 5 >> ${DNN_FILENAME}
    echo  >> ${DNN_FILENAME}
done

echo JOB C eval_model_dnn_${model_indices}.submit >> ${DNN_FILENAME}
echo SCRIPT PRE C eval_dnn_prescript_IN.sh ${model_indices} \$RETRY >> ${DNN_FILENAME}
echo SCRIPT POST C eval_dnn_postscript_IN.sh ${model_indices} dnn IN >> ${DNN_FILENAME}
echo RETRY C 5 >> ${DNN_FILENAME}
echo >> ${DNN_FILENAME}

echo PARENT B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 B11 B12 B13 B14 B15 B16 B17 B18 B19 CHILD C >> ${DNN_FILENAME}
echo >> ${DNN_FILENAME}

for i in {0..19}
do
    echo VARS B${i} modelidx=\"${model_indices}\" input_int=\"${i}\" >> ${DNN_FILENAME}
done
echo >> ${DNN_FILENAME}
echo VARS C modelidx=\"${model_indices}\" >> ${DNN_FILENAME}

# generate LRC workflow
LRC_DAG_FILE='workflow_lrc_IN.dag'
LRC_FILENAME='lrc/workflow_lrc_IN.dag'
if [ -f ${LRC_FILENAME} ]; then
    rm ${LRC_FILENAME}
fi

touch ${LRC_FILENAME}
for i in {0..19}
do
    echo JOB B${i} shallow_lrc_${i}.submit >> ${LRC_FILENAME}
    echo SCRIPT PRE B${i} lrc_prescript_IN.sh ${i} \$RETRY ${model_indices} >> ${LRC_FILENAME}
    echo SCRIPT POST B${i} lrc_postscript_IN.sh ${i} ${model_indices} >> ${LRC_FILENAME}
    echo RETRY B${i} 5 >> ${LRC_FILENAME}
    echo  >> ${LRC_FILENAME}
done

echo JOB C eval_model_lrc_only.submit >> ${LRC_FILENAME} 
echo SCRIPT PRE C eval_lrc_prescript_IN.sh ${model_indices} \$RETRY >> ${LRC_FILENAME}
echo SCRIPT POST C eval_lrc_postscript_IN.sh ${model_indices} lrc IN >> ${LRC_FILENAME}
echo RETRY C 5 >> ${LRC_FILENAME}
echo >> ${LRC_FILENAME}

echo PARENT B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 B11 B12 B13 B14 B15 B16 B17 B18 B19 CHILD C >> ${LRC_FILENAME}
echo >> ${LRC_FILENAME}

for i in {0..19}
do
    echo VARS B${i} modelidx=\"${model_indices}\" input_int=\"${i}\" >> ${LRC_FILENAME}
done

echo >> ${LRC_FILENAME}
echo VARS C modelidx=\"${model_indices}\" >> ${LRC_FILENAME}

# initialize variables for two jobs
DNN_JOB_ID=""
LRC_JOB_ID=""
dnn_flag=0
lrc_flag=0

# use this utility function to handle whatever cleanup is needed prior to exiting your job
cleanup_before_exit () {
    # do your thing here
    agave_log_response "Cleaning up ..." 
    msg="Remove jobs, dnn=$DNN_JOB_ID, lrc=$LRC_JOB_ID"
    agave_log_response $msg
    JOB_RESPONSE=$(condor_rm $DNN_JOB_ID)
    msg="DNN response: $JOB_RESPONSE"
    agave_log_response $msg
    JOB_RESPONSE=$(condor_rm $LRC_JOB_ID)
    msg="LRC response: $JOB_RESPONSE"
    agave_log_response $msg
}

job_submission () {
    JOB_RESPONSE=$(condor_submit_dag $1)
    agave_log_response $JOB_RESPONSE

    if [[ $JOB_RESPONSE =~ ^.*cluster ]]; then
	JOB_ID=$(echo $JOB_RESPONSE | sed -e 's/^.*cluster//g' -e 's/\..*//g')
	msg="Job id: $JOB_ID"
	agave_log_response $msg

	if [ -z "$JOB_ID" ]; then
	    agave_log_response "Unable to obtain job id from condor_submit_dag command. Job tracking is not possible."
	    cleanup_before_exit 
	    ${AGAVE_JOB_CALLBACK_FAILED}
	    exit 1;
	fi
    else
	agave_log_response "The job format may be changed. Unable to obtain job id from condor_submit_dag command. Job tracking is not possible."
	cleanup_before_exit 
	${AGAVE_JOB_CALLBACK_FAILED}
	exit 1;
    fi
}

job_monitoring () {
    flag=0

    # is job in queue at the moment
    is_queued=$(condor_q -format '%d' JobStatus $1)
    # msg="Queue: $is_queued"
    # echo $msg

    # if not, check to see what's up
    if [ -z "$is_queued" ]; then
	status=$(condor_history -format '%d' JobStatus $1)
	# msg="history status: $status"
	# echo $msg

        # condor daemon may not have record of the job. if so, just quit. nothing we can do here.
	if [ -z "$status" ]; then
	    agave_log_response "No record of the job on the remote Condor system. Assuming job deleted forcefully on the Condor system."
	    # echo $agave_log_response
	    cleanup_before_exit 
	    ${AGAVE_JOB_CALLBACK_FAILED}
	    kill -SIGQUIT $2
	    # ;;
	fi

	# we know the job isn't in queue, let's parse the response code to see why.
	case "$status" in
	    0)
		agave_log_response "Job failed to checkpoint. When it starts running, it will start running from the beginning";
		# echo $agave_log_response
		SECONDS_BETWEEN_CHECKS=300
		;;
	    1)  
		agave_log_response "Job is current in queue"
		# echo $agave_log_response
		;;
	    2)  
		agave_log_response "Job removed forcefully from the Condor system"
		# echo $agave_log_response
		cleanup_before_exit
		${AGAVE_JOB_CALLBACK_CLEANING_UP}
		exit 1
		;;
	    3)  
		agave_log_response "Job removed forcefully from the Condor system"
		# echo $agave_log_response
		cleanup_before_exit
		${AGAVE_JOB_CALLBACK_CLEANING_UP}
		exit 1
		;;
	    4)  
		agave_log_response "Job completed. Calling Agave for archiving and cleanup"
		# echo $agave_log_response
		# cleanup_before_exit
		# ${AGAVE_JOB_CALLBACK_CLEANING_UP}
		# exit 0
		flag=1
		;;
	    5)  
		agave_log_response "Job paused"
		# echo $agave_log_response
		SECONDS_BETWEEN_CHECKS=600
		;;
	    6)  
		agave_log_response "Job failed during submission by the Condor server"
		# echo $agave_log_response
		cleanup_before_exit
		${AGAVE_JOB_CALLBACK_FAILED}
		exit 1
		;;
	    *)  
		agave_log_response "Lost track of the job. Unexpected response ${status} from condor_history"
		# echo $agave_log_response
		cleanup_before_exit 
		exit 1
		;;
	esac
    fi    
    sleep $SECONDS_BETWEEN_CHECKS;
}

# submit the condor dag jobs
if [ -f ${DNN_FILENAME} ] && [ -f ${LRC_FILENAME} ]; then
   msg="File $DNN_FILENAME and $LRC_FILENAME exists."
   agave_log_response $msg
   # submit your dag file...calling it condor.dag for example.
   cd dnn
   chmod +x *prescript_IN.sh
   chmod +x *postscript_IN.sh
   job_submission $DNN_DAG_FILE 
   DNN_JOB_ID=$JOB_ID

   cd ../lrc
   chmod +x *prescript_IN.sh
   chmod +x *postscript_IN.sh
   job_submission $LRC_DAG_FILE 
   LRC_JOB_ID=$JOB_ID
   cd ..

   SECONDS_BETWEEN_CHECKS=30

   while true; 
   do 
       if [[ ("$dnn_flag" == 0) ]] ; then
	   # msg="dnn job ($DNN_JOB_ID) is monitored"
	   # echo $msg
	   job_monitoring $DNN_JOB_ID
	   dnn_flag=$flag
       fi

       if [[ ("$lrc_flag" == 0) ]] ; then
	   # msg="lrc job ($LRC_JOB_ID) is monitored"
	   # echo $msg
	   job_monitoring $LRC_JOB_ID
	   lrc_flag=$flag
       fi

       if [[ ("$dnn_flag" == 1) && ("$lrc_flag" == 1) ]] ; then
	   agave_log_response "both jobs are complete......"
	   # cleanup_before_exit

	   # populate job output into the database
	   x=$(find . -name "results_*.tgz")
	   agave_log_response $x
	   set -f
	   set -- $x
	   agave_log_response $#
	   if [ $# -eq 2 ]
	   then	      
	       agave_log_response "The job outputs are populated into the database" 
	       source /home/nsidescommunity/venv/bin/activate
	       python ./outputs_populate_agave.py --file-list "$x"
	       deactivate
	       ${AGAVE_JOB_CALLBACK_CLEANING_UP}
	       exit 0
	   else
	       agave_log_response "Unable to populate job outputs into the database since they are not generated correclty."
	       cleanup_before_exit 
	       ${AGAVE_JOB_CALLBACK_CLEANING_UP}
	       ${AGAVE_JOB_CALLBACK_FAILURE}
	       exit 1;	       
	   fi	   
       fi
       
   done

else
   msg="File, $DNN_FILENAME or $LRC_FILENAME does not exist."
   agave_log_response $msg
fi
