#!/bin/bash


#
# Advertise the k8s provisioner
#

if [ "x${K8S_PROVISIONER_TYPE}" != "x" ]; then
  echo "K8SProvisionerType=\"${K8S_PROVISIONER_TYPE}\"" >> "${PILOT_CONFIG_FILE}"
  echo 'STARTD_EXPRS = $(STARTD_EXPRS) K8SProvisionerType'  >> "${PILOT_CONFIG_FILE}"
fi

if [ "x${K8S_PROVISIONER_NAME}" != "x" ]; then
  echo "K8SProvisionerName=\"${K8S_PROVISIONER_NAME}\"" >> "${PILOT_CONFIG_FILE}"
  echo 'STARTD_EXPRS = $(STARTD_EXPRS) K8SProvisionerName'  >> "${PILOT_CONFIG_FILE}"
fi

