#!/bin/bash

# simple singularity wrapper that doesn't allow the -p or --pid option
# also rewrite -C to remove the -p option
# Disclaimer: Based on 
#  https://wiki-dev.bash-hackers.org/scripting/posparams
#

options=()  # the buffer array for the parameters
eoo=0       # end of options reached

while [[ $1 ]]
do
    if ! ((eoo)); then
	case "$1" in
	  --pid)
              # pretend was not passed
	      shift
	      ;;
          -p)
              # pretend was not passed
              shift
              ;;
          --containall)
              options+=("--contain")
              options+=("--cleanenv")
              options+=("--ipc")
              # but not --pid
              shift
              ;;
          -C)
              options+=("-c")
              options+=("-e")
              options+=("-i")
              # but not -p
              shift
              ;;
	  --)
	      eoo=1
	      options+=("$1")
	      shift
	      ;;
	  *)
	      options+=("$1")
	      shift
	      ;;
	esac
    else
	options+=("$1")
	shift
    fi
done

exec /usr/bin/singularity.org "${options[@]}"

