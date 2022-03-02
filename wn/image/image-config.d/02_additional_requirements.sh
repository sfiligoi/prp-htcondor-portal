#!/bin/bash

if [ "x${ADDITIONAL_REQUIREMENTS}" != "x" ]; then
  echo "# Additional requirements added at runtime " > /etc/condor/config.d/02-additional-reqs.conf
  echo "MATCHING_START = ( \$(MATCHING_START) ) && ( ${ADDITIONAL_REQUIREMENTS} )" >> /etc/condor/config.d/02-additional-reqs.conf
fi
