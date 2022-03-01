#!/bin/bash

if [ "x${K8S_NAMESPACE}" == "x" ]; then
  K8S_NAMESPACE=prp
fi
if [ "x${PHYSICAL_HOSTNAME}" == "x" ]; then
  PHYSICAL_HOSTNAME=me
fi
if [ "x${K8S_DOMAIN}" == "x" ]; then
  K8S_DOMAIN=optiputer.net
fi

# k8s nodes have no domain, which is annoying
# Add it here
cp /etc/hosts /tmp/hosts && sed "s/\(${HOSTNAME}\/\1\.${PHYSICAL_HOSTNAME}.${K8S_NAMESPACE}.${K8S_DOMAIN} \1/" /tmp/hosts > /etc/hosts && rm -f /tmp/hosts
