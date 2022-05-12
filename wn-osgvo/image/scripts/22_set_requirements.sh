#!/bin/bash

cat >>  "${PILOT_CONFIG_FILE}" << EOF
#
# Force matching on K8SNamespace
# unless FORCE_K8SNAMESPACE_MATCHING=="no"
#

FORCE_K8SNAMESPACE_MATCHING = "${FORCE_K8SNAMESPACE_MATCHING:-no}"
STARTD_EXPRS = \$(STARTD_EXPRS) FORCE_K8SNAMESPACE_MATCHING

MATCHING_START = ( (FORCE_K8SNAMESPACE_MATCHING=?="no") || regexp(TARGET.RequestK8SNamespace,K8SNamespace) )

#
# Force matching on provisioned resources
#

PROVISIONING_START = ifthenelse(TARGET.RequestCPUs=!=undefined, CPUs=?=TARGET.RequestCPUs, CPUs=?=1)

# Pretend small memory and disk requests are the equivalent of not set
PROVISIONING_START = \$(PROVISIONING_START) && \\
                     ifthenelse(TARGET.RequestMemory=!=undefined, ifthenelse(TARGET.RequestMemory<4096,Memory=?=4096, Memory=?=TARGET.RequestMemory), Memory=?=4096)
PROVISIONING_START = \$(PROVISIONING_START) && \\
                     ifthenelse(TARGET.RequestDisk=!=undefined, ifthenelse(TARGET.RequestDisk<8000000,Disk=?=8000000, Disk=?=TARGET.RequestDisk), Disk=?=8000000)

# GPUs will not be defined if there are no GPUs
PROVISIONING_START = \$(PROVISIONING_START) && \\
                     ifthenelse(TARGET.RequestGPUs=!=undefined, \\
                                ifthenelse(GPUs=!=undefined, GPUs=?=TARGET.RequestGPUs, TARGET.RequestGPUs=?=0), \\
                                (GPUs=?=undefined) || (GPUs=?=0))

START = ( \$(START) ) && ( \$(PROVISIONING_START) ) && ( \$(MATCHING_START) )

EOF


if [ "x${ADDITIONAL_REQUIREMENTS}" != "x" ]; then
  echo "# Additional requirements added at runtime " > "${PILOT_CONFIG_FILE}"
  echo "MATCHING_START = ( \$(MATCHING_START) ) && ( ${ADDITIONAL_REQUIREMENTS} )" >> "${PILOT_CONFIG_FILE}"
fi
