#!/bin/bash

if [ "x${NVIDIA_SYMLINK}" == "xyes" ]; then
  # some environments have NVIDIA tools in non-standard locations

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
fi

