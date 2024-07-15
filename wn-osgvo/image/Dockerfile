FROM opensciencegrid/osgvo-docker-pilot:23-el9-release

# Fix python vs python3
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10

# Tweaked singularity for container environments
# Remove default singularity from path, too
COPY scripts/singularity_npid.sh /usr/bin/singularity_npid.sh
RUN mv /usr/bin/singularity /usr/bin/singularity.org && \
    chmod a+x /usr/bin/singularity_npid.sh && \
    ln -s /usr/bin/singularity_npid.sh /usr/bin/singularity

COPY scripts/apptainer_npid.sh /usr/bin/apptainer_npid.sh
RUN mv /usr/bin/apptainer /usr/bin/apptainer.org && \
    chmod a+x /usr/bin/apptainer_npid.sh && \
    ln -s /usr/bin/apptainer_npid.sh /usr/bin/apptainer

# We want to be able to add system-level changes
# and run without explicit privilege drop
RUN mv /usr/local/sbin/entrypoint.sh /usr/local/sbin/entrypoint.osg.sh
COPY scripts/entrypoint.sh /usr/local/sbin/entrypoint.sh
RUN chmod a+rx /usr/local/sbin/entrypoint.sh

COPY scripts/check_master.sh /bin/check_master.sh
RUN chmod a+rx /bin/check_master.sh

# system level scripts
COPY scripts/01_token.sh /etc/entrypoint/image-config.d/01_token.sh
COPY scripts/01_no_condor_host.sh /etc/entrypoint/image-config.d/01_no_condor_host.sh

# pilot level scripts
COPY scripts/02_validate_singularity.sh /etc/osg/image-init.d/02_validate_singularity.sh 
COPY scripts/02_validate_apptainer.sh /etc/osg/image-init.d/02_validate_apptainer.sh 
COPY scripts/19_set_resources.sh /etc/osg/image-init.d/19_set_resources.sh
COPY scripts/20_advertise_glidein.sh /etc/osg/image-init.d/20_advertise_glidein.sh
COPY scripts/20_advertise_k8s_domain.sh /etc/osg/image-init.d/20_advertise_k8s_domain.sh
COPY scripts/21_advertise_k8s_provisioner.sh  /etc/osg/image-init.d/21_advertise_k8s_provisioner.sh
COPY scripts/22_set_requirements.sh /etc/osg/image-init.d/22_set_requirements.sh

# keep default low, as we expect to be running in opportunistic mode
env ACCEPT_JOBS_FOR_HOURS=24

# keep default idle time low, as we may over-provision certain kinds of resources
# but others may be waiting
env ACCEPT_IDLE_MINUTES=20

#
# In addition to osgvo-docker-pilot envs,
# it accepts also the following env variables
# NUM_CPUS MEMORY DISK NUM_GPUS
# PHYSICAL_HOSTNAME
# K8S_NAMESPACE K8S_DOMAIN
# K8S_PROVISIONER_NAME K8S_PROVISIONER_TYPE
# FORCE_K8SNAMESPACE_MATCHING ADDITIONAL_REQUIREMENTS
#

