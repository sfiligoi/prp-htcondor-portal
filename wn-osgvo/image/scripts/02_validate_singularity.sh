#!/bin/bash

# check if we need to test nvidia
nvf=
ls -l /dev/nvidia*
if [ $? -eq 0 ]; then
  nvf=--nv
fi

# else do nothing, let Condor figure it out

if [ -f "/usr/bin/singularity" ]; then
  # only test for singularity functionality if singularity is present
  # may not be in all pods

  /usr/bin/singularity exec $nvf --contain --ipc --pid --bind /cvmfs /cvmfs/singularity.opensciencegrid.org/opensciencegrid/osgvo-el8:latest /usr/bin/dc -e "3 5 + p"
  rc=$?

  if [ $rc -ne 0 ]; then
    echo "Singularity test execution failed!"
    sleep 30
    exit 1
  fi

fi
