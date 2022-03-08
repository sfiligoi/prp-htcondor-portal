#!/bin/bash
su provisioner -c "touch /home/provisioner/.bashrc"

su provisioner -c "echo export KUBERNETES_SERVICE_PORT=${KUBERNETES_SERVICE_PORT} >> /home/provisioner/.bashrc"
su provisioner -c "echo export KUBERNETES_SERVICE_HOST=${KUBERNETES_SERVICE_HOST} >> /home/provisioner/.bashrc"
