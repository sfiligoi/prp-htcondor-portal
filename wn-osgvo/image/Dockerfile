FROM opensciencegrid/osgvo-docker-pilot:3.6-release

# Tweaked singularity for container environments
# Remove default singularity from path, too
COPY scripts/singularity_npid.sh /usr/bin/singularity_npid.sh
RUN mv /usr/bin/singularity /usr/bin/singularity.org && \
    chmod a+x /usr/bin/singularity_npid.sh && \
    ln -s /usr/bin/singularity_npid.sh /usr/bin/singularity

# We want to be able to add system-level changes
# and run without explicit privilege drop
RUN mv /bin/entrypoint.sh /bin/entrypoint.osg.sh
COPY scripts/entrypoint.sh /bin/entrypoint.sh
RUN chmod a+rx /bin/entrypoint.sh

COPY scripts/19_set_resources.sh /etc/osg/image-init.d/19_set_resources.sh
COPY scripts/20_advertise_k8s_domain.sh /etc/osg/image-init.d/20_advertise_k8s_domain.sh
COPY scripts/21_advertise_k8s_provisioner.sh  /etc/osg/image-init.d/21_advertise_k8s_provisioner.sh
COPY scripts/22_set_requirements.sh /etc/osg/image-init.d/22_set_requirements.sh


#
# In addition to osgvo-docker-pilot envs,
# it accepts also the following env variables
# CONDOR_HOST
# NUM_CPUS MEMORY DISK NUM_GPUS
# PHYSICAL_HOSTNAME
# K8S_NAMESPACE K8S_DOMAIN
# K8S_PROVISIONER_NAME K8S_PROVISIONER_TYPE
# FORCE_K8SNAMESPACE_MATCHING ADDITIONAL_REQUIREMENTS
#

