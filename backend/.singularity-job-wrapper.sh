#!/bin/bash

function getPropBool
{
    # $1 the file (for example, $_CONDOR_JOB_AD or $_CONDOR_MACHINE_AD)
    # $2 the key
    # $3 is the default value if unset
    # echo "1" for true, "0" for false/unspecified
    # return 0 for true, 1 for false/unspecified
    default=$3
    if [ "x$default" = "x" ]; then
        default=0
    fi
    val=`(grep -i "^$2 " $1 | cut -d= -f2 | sed "s/[\"' \t\n\r]//g") 2>/dev/null`
    # convert variations of true to 1
    if (echo "x$val" | grep -i true) >/dev/null 2>&1; then
        val="1"
    fi
    if [ "x$val" = "x" ]; then
        val="$default"
    fi
    echo $val
    # return value accordingly, but backwards (true=>0, false=>1)
    if [ "$val" = "1" ];  then
        return 0
    else
        return 1
    fi
}


function getPropStr
{
    # $1 the file (for example, $_CONDOR_JOB_AD or $_CONDOR_MACHINE_AD)
    # $2 the key
    # $3 default value if unset
    default="$3"
    val=`(grep -i "^$2 " $1 | cut -d= -f2 | sed "s/[\"' \t\n\r]//g") 2>/dev/null`
    if [ "x$val" = "x" ]; then
        val="$default"
    fi
    echo $val
}


if [ "x$_CONDOR_JOB_AD" = "x" ]; then
    export _CONDOR_JOB_AD="NONE"
fi
if [ "x$_CONDOR_MACHINE_AD" = "x" ]; then
    export _CONDOR_MACHINE_AD="NONE"
fi

# make sure the job can access certain information via the environment, for example ProjectName
export OSGVO_PROJECT_NAME=$(getPropStr $_CONDOR_JOB_AD ProjectName)
export OSGVO_SUBMITTER=$(getPropStr $_CONDOR_JOB_AD User)

# "save" some setting from the condor ads - we need these even if we get re-execed
# inside singularity in which the paths in those env vars are wrong
# Seems like arrays do not survive the singularity transformation, so set them
# explicity

export HAS_SINGULARITY=$(getPropBool $_CONDOR_MACHINE_AD HAS_SINGULARITY 0)
export OSG_SINGULARITY_PATH="/usr/bin/singularity"
export OSG_SINGULARITY_IMAGE_DEFAULT="/cvmfs/singularity.opensciencegrid.org/opensciencegrid/tensorflow-gpu:latest"
export OSG_SINGULARITY_IMAGE=$(getPropStr $_CONDOR_JOB_AD SingularityImage)
export OSG_SINGULARITY_BIND_CVMFS=1
export OSG_SINGULARITY_BIND_GPU_LIBS=1

export OSG_MACHINE_GPUS=$(getPropStr $_CONDOR_MACHINE_AD GPUs "0")

#############################################################################
#
#  Singularity
#
if [ "x$HAS_SINGULARITY" = "x1" -a "x$OSG_SINGULARITY_PATH" != "x" -a "x$OSG_SINGULARITY_IMAGE" != "x" ]; then

    # put a human readable version of the image in the env before
    # expanding it - useful for monitoring
    export OSG_SINGULARITY_IMAGE_HUMAN="$OSG_SINGULARITY_IMAGE"

    # for /cvmfs based directory images, expand the path without symlinks so that
    # the job can stay within the same image for the full duration
    if echo "$OSG_SINGULARITY_IMAGE" | grep /cvmfs >/dev/null 2>&1; then
        if (cd $OSG_SINGULARITY_IMAGE) >/dev/null 2>&1; then
            NEW_IMAGE_PATH=`(cd $OSG_SINGULARITY_IMAGE && pwd -P) 2>/dev/null`
            if [ "x$NEW_IMAGE_PATH" != "x" ]; then
                OSG_SINGULARITY_IMAGE="$NEW_IMAGE_PATH"
            fi
        fi
    fi
    
    OSG_SINGULARITY_EXTRA_OPTS=""

    # cvmfs access inside container (default, but optional)
    if [ "x$OSG_SINGULARITY_BIND_CVMFS" = "x1" ]; then
        OSG_SINGULARITY_EXTRA_OPTS="$OSG_SINGULARITY_EXTRA_OPTS --bind /cvmfs"
    fi
    
    # GPUs - bind outside GPU library directory to inside /host-libs
    if [ $OSG_MACHINE_GPUS -gt 0 ]; then
        if [ "x$OSG_SINGULARITY_BIND_GPU_LIBS" = "x1" ]; then
            HOST_LIBS=""
            if [ -e "/usr/lib64/nvidia" ]; then
                HOST_LIBS=/usr/lib64/nvidia
            fi
            if [ "x$HOST_LIBS" != "x" ]; then
                OSG_SINGULARITY_EXTRA_OPTS="$OSG_SINGULARITY_EXTRA_OPTS --bind $HOST_LIBS:/host-libs"
            fi
        fi
    else
        # if not using gpus, we can limit the image more
        OSG_SINGULARITY_EXTRA_OPTS="$OSG_SINGULARITY_EXTRA_OPTS --contain"
    fi

    # We want to bind $PWD to /srv within the container - however, in order
    # to do that, we have to make sure everything we need is in $PWD, most
    # notably the user-job-wrapper.sh (this script!)
    cp $0 .singularity-job-wrapper.sh

    # Remember what the outside pwd dir is so that we can rewrite env vars
    # pointing to omewhere inside that dir (for example, X509_USER_PROXY)
    if [ "x$_CONDOR_JOB_IWD" != "x" ]; then
        export OSG_SINGULARITY_OUTSIDE_PWD="$_CONDOR_JOB_IWD"
    else
        export OSG_SINGULARITY_OUTSIDE_PWD="$PWD"
    fi

    # build a new command line, with updated paths
    CMD=()
    for VAR in "$@"; do
        # Two seds to make sure we catch variations of the iwd,
        # including symlinked ones. The leading space is to prevent
        # echo to interpret dashes.
        VAR=`echo " $VAR" | sed -E "s;$PWD(.*);/srv\1;" | sed -E "s;.*/execute/dir_[0-9a-zA-Z]*(.*);/srv\1;" | sed -E "s;^ ;;"`
        CMD+=("$VAR")
    done

    exec $OSG_SINGULARITY_PATH exec $OSG_SINGULARITY_EXTRA_OPTS \
                               --home $PWD:/srv \
                               --pwd /srv \
                               --scratch /var/tmp \
                               --scratch /tmp \
                               --ipc --pid \
                               "$OSG_SINGULARITY_IMAGE" \
                               "${CMD[@]}"

    
fi

#############################################################################
#
#  Run the real job
#
exec "$@"
error=$?
echo "Failed to exec($error): $@" > $_CONDOR_WRAPPER_ERROR_FILE
exit 1