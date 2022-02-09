#!/bin/bash

# starting with cuda-11, the nvidia/cuda bins and libs are not in he defaul pahs anymore
# create symlinks as a short-term fix to ensure backward compatibilitty

for d in /usr/local/nvidia/bin 
do
  pushd $d
  for f in *; do
    ln -s $d/$f /bin/$f
  done
  popd
done

for d in /usr/local/nvidia/lib64 /usr/local/cuda/lib64
do
  pushd $d
  for f in *so*; do
    ln -s $d/$f /usr/lib64/$f
  done
  popd
done

exit 0
