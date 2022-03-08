#!/bin/bash
su provisioner -c "mkdir -p /home/provisioner/.condor/tokens.d && chmod -R go-rwx /home/provisioner/.condor"
cp /etc/condor/tokens.d/* /home/provisioner/.condor/tokens.d/ && chown -R provisioner /home/provisioner/.condor

