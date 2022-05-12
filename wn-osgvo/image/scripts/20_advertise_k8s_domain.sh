#!/bin/bash


#
# Advertise the k8s namespace and physical hostname
#

echo "# K8S params" >> "${PILOT_CONFIG_FILE}"

if [ "x${HOSTNAME}" != "x" ]; then
  echo "K8SPodName=\"${HOSTNAME}\"" >> "${PILOT_CONFIG_FILE}"
  echo 'STARTD_EXPRS = $(STARTD_EXPRS) K8SPodName'  >> "${PILOT_CONFIG_FILE}"
fi

if [ "x${K8S_DOMAIN}" != "x" ]; then
  echo "K8SDomain=\"${K8S_DOMAIN}\"" >> "${PILOT_CONFIG_FILE}"
  echo 'STARTD_EXPRS = $(STARTD_EXPRS) K8SDomain'  >> "${PILOT_CONFIG_FILE}"
fi

if [ "x${K8S_NAMESPACE}" != "x" ]; then
  echo "K8SNamespace=\"${K8S_NAMESPACE}\"" >> "${PILOT_CONFIG_FILE}"
  echo 'STARTD_EXPRS = $(STARTD_EXPRS) K8SNamespace'  >> "${PILOT_CONFIG_FILE}"
fi

if [ "x${PHYSICAL_HOSTNAME}" != "x" ]; then
  echo "K8SPhysicalHostName=\"${PHYSICAL_HOSTNAME}\"" >> "${PILOT_CONFIG_FILE}"
  echo 'STARTD_EXPRS = $(STARTD_EXPRS) K8SPhysicalHostName'  >> "${PILOT_CONFIG_FILE}"
fi

