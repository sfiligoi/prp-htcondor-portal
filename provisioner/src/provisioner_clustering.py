#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi 2021
#
# Implement the clusterinng
#

from collections import OrderedDict
import copy
import re

#
# GPUTypes is a comma-separated list of GPU names
# Note: The GPUType is just a special case of a label
#       with the hardcoded key of gpu-type
#
# DiskVolumes are an encoded comma-separated list
# with each element a colon separated pair
#   PVC_NAME:MOUNT_PATH
#
# Labels are an encoded comma-separated list
# with each element a colon spearated pair
#   LABEL_KEY:LABEL_VALUE
#

class ProvisionerClusteringAttributes:

   def __init__(self):
      self.attributes=OrderedDict()
      self.attributes['Namespace']=None # fail is not specified 
      self.attributes['CPUs']=1
      self.attributes['Memory']=1024
      self.attributes['Disk']=100000
      self.attributes['DiskVolumes']=''
      self.attributes['GPUs']=0
      self.attributes['GPUTypes']=''
      self.attributes['Labels']=''

   def expand_schedd_attr(self, attr):
      return "Request%s"%attr

   def get_schedd_attributes(self):
      attrs=[]
      for k in self.attributes.keys():
        attrs.append(self.expand_schedd_attr(k))
      return attrs

   def expand_startd_attr(self, attr):
      return "Provisioned%s"%attr

   def get_startd_attributes(self):
      attrs=[]
      for k in self.attributes.keys():
        attrs.append(self.expand_startd_attr(k))
      return attrs

   def expand_k8s_attr(self, attr):
      return "Pod%s"%attr

   def get_k8s_attributes(self):
      attrs=[]
      for k in self.attributes.keys():
        if k=="Namespace":
           continue # namespace is native to k8s
        attrs.append(self.expand_k8s_attr(k))
      return attrs


class ProvisionerCluster:
   def __init__(self, key, attr_vals):
      self.key = key
      self.attr_vals = attr_vals
      self.elements = []

   def append(self, el):
      self.elements.append(el)


class ProvisionerScheddCluster(ProvisionerCluster):
   def __init__(self, key, attr_vals, schedd_attrs):
      ProvisionerCluster.__init__(self, key, attr_vals)
      self.schedd_attrs = schedd_attrs

   def count_idle(self):
      cnt = 0
      for job in self.elements:
         status="%s"%job['JobStatus']
         if status=="1":
            cnt+=1
      return cnt

class ProvisionerClustering:
   def __init__(self):
      self.attrs=ProvisionerClusteringAttributes()

   def cluster_schedd_jobs(self, schedd_jobs):
      clusters={}
      for job in schedd_jobs:
         job_attrs=[]
         key_attrs={}
         for k in self.attrs.attributes.keys():
            jobk = self.attrs.expand_schedd_attr(k)
            if jobk in job.keys():
               val = job[jobk]
            else:
               val = self.attrs.attributes[k]
            job_attrs.append("%s"%val)
            key_attrs[jobk]=val
         job_key=";".join(job_attrs)
         if job_key not in clusters:
            clusters[job_key] = ProvisionerScheddCluster(job_key, job_attrs, key_attrs)
         clusters[job_key].append(job)
         # cleanup to avoid accidental reuse
         del job_attrs
         del key_attrs

      return clusters
 
