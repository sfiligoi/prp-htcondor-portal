#!/bin/bash

#
# Adapted from https://github.com/htcondor/htcondor/blob/master/build/docker/services/base/start.sh
#

prog=${0##*/}
progdir=${0%/*}

fail () {
    echo "$prog:" "$@" >&2
    exit 1
}

add_values_to () {
    config=$1
    shift
    printf "%s=%s\n" >> "/etc/condor/config.d/$config" "$@"
}

full_num_cpus="${NUM_CPUS:-1}"
full_memory="${MEMORY:-1024}"
full_disk="${DISK:-100000}"
full_num_gpus="${NUM_GPUS:-0}"

# Create a config file from the environment.
# The config file needs to be on disk instead of referencing the env
# at run time so condor_config_val can work.
echo "# This file was created by $prog" > /etc/condor/config.d/01-env.conf
add_values_to 01-env.conf \
    CONDOR_HOST "${CONDOR_SERVICE_HOST:-${CONDOR_HOST:-\$(FULL_HOSTNAME)}}" \
    USE_POOL_PASSWORD "${USE_POOL_PASSWORD:-no}" \
    NUM_CPUS "${full_num_cpus}" \
    MEMORY "${full_memory}" \
    DISK "${full_disk}"

# single slot using all the requested resources
echo "NUM_SLOTS_TYPE_1 = 1" >> /etc/condor/config.d/01-env.conf
if [ "x${full_num_gpus}" != "x0" ]; then
   # we cannot really set the number of GPUs, just enable auto-detect
   echo "use feature : GPUs" >> /etc/condor/config.d/01-env.conf
   echo "SLOT_TYPE_1 = cpu=${full_num_cpus},mem=${full_memory},disk=auto,swap=auto,gpus=${full_num_gpus}" \
      >> /etc/condor/config.d/01-env.conf
else
   echo "SLOT_TYPE_1 = cpu=${full_num_cpus},mem=${full_memory},disk=auto,swap=auto" \
      >> /etc/condor/config.d/01-env.conf
fi


if [ "x${STARTD_NOCLAIM_SHUTDOWN}" != "x" ]; then
  echo "# This file was created by $prog" > /etc/condor/config.d/01-noclaim-shutdown.conf
  add_values_to 01-noclaim-shutdown.conf \
      STARTD_NOCLAIM_SHUTDOWN "${STARTD_NOCLAIM_SHUTDOWN}"
fi

echo "# This file was created by $prog" > /etc/condor/config.d/02-k8s-env.conf
echo 'STARTD_EXPRS = $(STARTD_EXPRS) K8SNamespace K8SDomain K8SPodName' \
  >> /etc/condor/config.d/02-k8s-env.conf

add_values_to 01-k8s-env.conf \
    K8SProvisionerType "\"${K8S_PROVISIONER_TYPE:-PRPHTCondorProvisioner}\"" \
    K8SProvisionerName "\"${K8S_PROVISIONER_NAME:-Unknown}\"" \
    K8SNamespace "\"${K8S_NAMESPACE:-Invalid}\"" \
    K8SDomain "\"${K8S_DOMAIN:-Unknown}\"" \
    K8SPodName "\"${HOSTNAME:-Unknown}\""

# Bug workaround: daemons will die if they can't raise the number of FD's;
# cap the request if we can't raise it.
hard_max=$(ulimit -Hn)

rm -f /etc/condor/config.d/01-fdfix.conf
# Try to raise the hard limit ourselves.  If we can't raise it, lower
# the limits in the condor config to the maximum allowable.
for attr in COLLECTOR_MAX_FILE_DESCRIPTORS \
            SHARED_PORT_MAX_FILE_DESCRIPTORS \
            SCHEDD_MAX_FILE_DESCRIPTORS \
            MAX_FILE_DESCRIPTORS; do
    config_max=$(condor_config_val -evaluate $attr 2>/dev/null)
    if [[ $config_max =~ ^[0-9]+$ && $config_max -gt $hard_max ]]; then
        if ! ulimit -Hn "$config_max" &>/dev/null; then
            add_values_to 01-fdfix.conf "$attr" "$hard_max"
        fi
        ulimit -Hn "$hard_max"
    fi
done
[[ -s /etc/condor/config.d/01-fdfix.conf ]] && \
    echo "# This file was created by $prog" >> /etc/condor/config.d/01-fdfix.conf

# Allow the derived images to run any additional runtime customizations
for x in /etc/constainer_startup/image-config.d/*.sh; do source "$x"; done

if [[ -f /root/config/pre-exec.sh ]]; then
    bash -x /root/config/pre-exec.sh
fi


# properly cleanup on signal
trap 'echo signal received!; kill $(jobs -p); wait' SIGINT SIGTERM

# Do not accept more jobs after MASTER_PEACEFUL_SHUTDOWN seconds
# This way other users/pods get a chance to use these resources
# (if no-one else is requesting, we will get them back in a new pod)
mps="${MASTER_PEACEFUL_SHUTDOWN:-7200}"
(sleep ${mps}; condor_off -master -peaceful; echo "`date` Sending peaceful shutdown") &

# we want to live only as long as htcondor is alive
echo "`date` Starting condor_master"
/usr/sbin/condor_master -f&

wait $!
rc=$?
echo "`date` End of condor_master, rc=${rc}"

echo "=== tail /var/log/condor/MasterLog"
tail -100 /var/log/condor/MasterLog

echo "=== tail /var/log/condor/StartLog"
tail -100 /var/log/condor/StartLog

echo "========= startd_history ============="
cat /var/log/condor/startd_history
echo "========== end history  =============="

exit ${rc}
