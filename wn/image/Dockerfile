FROM nvidia/cuda:11.3.1-base-centos7

# OSG RPMs
RUN yum -y install https://repo.opensciencegrid.org/osg/3.6/osg-3.6-el7-release-latest.rpm && \
    yum -y install epel-release \
                   yum-plugin-priorities && \
    yum -y install less which \
                   osg-wn-client \
                   redhat-lsb-core && \
    yum -y install singularity && \
    yum -y install condor && \
    yum clean all

# Enable OpenCL
# As suggested by https://github.com/WIPACrepo/pyglidein/blob/master/Dockerfile
RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd

# Some helper OpenCL tools
RUN yum install -y clinfo && \
    yum clean all

# Condor does not pick up the system libraries
ADD profile.d/cudalib.sh /etc/profile.d/

# Root-less singularity
ADD scripts/singularity_npid.sh /usr/bin/singularity_npid.sh


ADD condor.d/* /etc/condor/config.d/

ADD scripts/container_startup.sh /usr/sbin/container_startup.sh
RUN chmod a+rx /usr/sbin/container_startup.sh

#
# Accepts env variables
# CONDOR_HOST NUM_CPUS MEMORY RESERVED_DISK STARTD_NOCLAIM_SHUTDOWN
#

CMD ["/usr/sbin/container_startup.sh"]
