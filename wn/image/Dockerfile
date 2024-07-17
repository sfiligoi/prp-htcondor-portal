FROM nvidia/cuda:12.1.0-base-rockylinux8

# Enable OpenCL
# As suggested by https://github.com/WIPACrepo/pyglidein/blob/master/Dockerfile
RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd

# OSG RPMs
RUN yum -y install https://repo.opensciencegrid.org/osg/23-main/osg-23-main-el8-release-latest.rpm && \
    yum -y install epel-release && \
    dnf config-manager --set-enabled powertools

RUN yum -y install less which procps-ng bind-utils \
                   osg-wn-client &&\
    yum -y install apptainer && \
    yum -y install condor condor-stash-plugin && \
    yum install -y clinfo && \
    yum clean all

# Install often used libraries
# Suggested RPMs from https://hub.docker.com/r/opensciencegrid/osgvo-el7/dockerfile
# At least one IceCube job types need freetype
# attr needed by CVMFS checks
RUN yum -y groupinstall "Development Tools" \
                        "Scientific Support" && \
    yum install -y freetype attr && \
    yum clean all

# Set python to be python3
RUN alternatives --set python /usr/bin/python3

# Condor does not pick up the system libraries
ADD profile.d/cudalib.sh /etc/profile.d/

# Tweaked singularity for container environments
# Remove default singularity from path, too
ADD scripts/singularity_npid.sh /usr/bin/singularity_npid.sh
RUN if [ -f /usr/bin/singularity ]; then mv /usr/bin/singularity /usr/bin/singularity.org; fi

ADD scripts/apptainer_npid.sh /usr/bin/apptainer_npid.sh
RUN mv /usr/bin/apptainer /usr/bin/apptainer.org

ADD condor.d/* /etc/condor/config.d/

ADD scripts/container_startup.sh /usr/sbin/container_startup.sh
RUN chmod a+rx /usr/sbin/container_startup.sh

# Additional stratup scripts can be uploaded here
# plus historic hack around a typo
RUN mkdir -p /etc/container_startup/image-config.d; \
    ln -s /etc/container_startup /etc/constainer_startup

ADD image-config.d/* /etc/container_startup/image-config.d/

RUN groupadd -g 3001 htcuser && useradd -u 3001 -g 3001 -s /usr/bin/bash htcuser

#
# Accepts env variables
# CONDOR_HOST
# STARTD_NOCLAIM_SHUTDOWN MASTER_PEACEFUL_SHUTDOWN
# NUM_CPUS MEMORY DISK NUM_GPUS
# PHYSICAL_HOSTNAME
# K8S_NAMESPACE K8S_DOMAIN
# K8S_PROVISIONER_NAME K8S_PROVISIONER_TYPE
# NVIDIA_SYMLINK
# FORCE_K8SNAMESPACE_MATCHING ADDITIONAL_REQUIREMENTS
#

CMD ["/usr/sbin/container_startup.sh"]
