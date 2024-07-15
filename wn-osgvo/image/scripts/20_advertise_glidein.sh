#!/bin/bash


#
# Advertise that this is a glidein
#

if [ "x${ADVERTISE_IS_GLIDEIN}" != "xN" ]; then
  echo "IS_GLIDEIN = true" >> "${PILOT_CONFIG_FILE}"
  echo 'STARTD_EXPRS = $(STARTD_EXPRS) IS_GLIDEIN'  >> "${PILOT_CONFIG_FILE}"
fi


