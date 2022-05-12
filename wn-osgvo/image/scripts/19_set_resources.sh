#!/bin/bash


#
# Advertise the k8s namespace and physical hostname
#

#
# NUM_CPUS and MEMORY are also handled by the osgvo-pilot
# but we re-set it here
#

full_num_cpus="${NUM_CPUS:-1}"
full_memory="${MEMORY:-1024}"
full_disk="${DISK:-100000}"
full_num_gpus="${NUM_GPUS:-0}"

echo "NUM_CPUS = ${full_num_cpus}" >> "${PILOT_CONFIG_FILE}"
echo "MEMORY = ${full_memory}" >> "${PILOT_CONFIG_FILE}"
echo "DISK = ${full_disk}" >> "${PILOT_CONFIG_FILE}"

# single slot using all the requested resources
echo "NUM_SLOTS_TYPE_1 = 1" >> "${PILOT_CONFIG_FILE}"
echo "SLOT_TYPE_1_PARTITIONABLE = FALSE" >> "${PILOT_CONFIG_FILE}"

if [ "x${full_num_gpus}" != "x0" ]; then
   # we cannot really set the number of GPUs, just enable auto-detect
   echo "use feature : GPUs" >> "${PILOT_CONFIG_FILE}"
   echo "SLOT_TYPE_1 = cpu=${full_num_cpus},mem=${full_memory},disk=auto,swap=auto,gpus=${full_num_gpus}" \
      >> "${PILOT_CONFIG_FILE}"
else
   echo "SLOT_TYPE_1 = cpu=${full_num_cpus},mem=${full_memory},disk=auto,swap=auto" \
      >> "${PILOT_CONFIG_FILE}"
fi

