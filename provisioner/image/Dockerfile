FROM centos:centos7

# OSG RPMs
RUN yum -y install https://repo.opensciencegrid.org/osg/3.6/osg-3.6-el7-release-latest.rpm && \
    yum -y install epel-release \
                   yum-plugin-priorities && \
    yum -y install less which \
                   redhat-lsb-core && \
    yum -y install python3-pip && \
    yum -y install condor python3-condor && \
    yum clean all

RUN pip3 install kubernetes


