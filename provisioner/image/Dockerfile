FROM centos:centos7

# OSG RPMs
RUN yum -y install https://repo.opensciencegrid.org/osg/3.6/osg-3.6-el7-release-latest.rpm && \
    yum -y install epel-release \
                   yum-plugin-priorities && \
    yum -y install less which \
                   redhat-lsb-core && \
    yum -y install python3-pip git && \
    yum -y install condor python3-condor && \
    yum clean all


RUN pip3 install kubernetes


# configure python packages
RUN mkdir -p /opt/provisioner && cd /opt/provisioner && git clone https://github.com/sfiligoi/prp-htcondor-portal.git && cd prp-htcondor-portal && git checkout main

RUN useradd provisioner && chown -R provisioner /opt/provisioner

RUN su provisioner -c '/usr/bin/ln -s /opt/provisioner/prp-htcondor-portal/provisioner/python/prp_provisioner /home/provisioner/prp_provisioner'

ADD provisioner_main.py /home/provisioner/provisioner_main.py
RUN chown provisioner /home/provisioner/provisioner_main.py

ADD setup_k8s_creds.sh /opt/provisioner/setup_k8s_creds.sh
ADD setup_htcondor_creds.sh /opt/provisioner/setup_htcondor_creds.sh
ADD provisioner_startup.sh /opt/provisioner/provisioner_startup.sh

#
# Requires env variables
# K8S_NAMESPACE
#
# Optionally
# CONDOR_HOST
#

CMD ["/opt/provisioner/provisioner_startup.sh"]
