#!/bin/bash

# basic setup
/opt/provisioner/setup_k8s_creds.sh
/opt/provisioner/setup_htcondor_creds.sh

mkdir -p /var/log/provisioner/logs
chown provisioner:provisioner /var/log/provisioner/logs

if [ "x${CONDOR_HOST}" == "x" ]; then
  echo "Using default CONDOR_HOST=prp-cm-htcondor.htcondor-portal.svc.cluster.local"
  export CONDOR_HOST=prp-cm-htcondor.htcondor-portal.svc.cluster.local
fi

if [ "x${K8S_NAMESPACE}" == "x" ]; then
  echo "Missing K8S_NAMESPACE"
  sleep 15
  exit 1
fi

echo "CONDOR_HOST=${CONDOR_HOST}" > /etc/condor/config.d/02_condor_host.config

echo "[DEFAULT]" > /home/provisioner/pod.conf
echo "condor_host=${CONDOR_HOST}" >> /home/provisioner/pod.conf
echo "namespace=${K8S_NAMESPACE}" >> /home/provisioner/pod.conf

trap 'echo signal received!; kill $(jobs -p); wait' SIGINT SIGTERM

echo "`date` Starting provisioner_main.py"
su provisioner -c "cd /home/provisioner && python3 provisioner_main.py /var/log/provisioner/logs/provisioner.log ${K8S_NAMESPACE}" &
wait
rc=$?
echo "`date` End of provisioner_main.py, rc=${rc}"

