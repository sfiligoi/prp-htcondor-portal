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
import datetime

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
      self.attributes['CPUs']=1
      self.attributes['Memory']=4096
      self.attributes['Disk']=8000000
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

   # Note: The startd attributes have no prefix

   def expand_k8s_attr(self, attr):
      return "Pod%s"%attr

   def get_k8s_attributes(self):
      attrs=[]
      for k in self.attributes.keys():
        attrs.append(self.expand_k8s_attr(k))
      return attrs


class ProvisionerCluster:
   def __init__(self, key, attr_vals):
      self.key = key
      self.attr_vals = attr_vals
      self.elements = []

   def append(self, el):
      self.elements.append(el)

   def append_list(self, ellist):
      for el in ellist:
        self.elements.append(el)

   def get_attr_dict(self):
      p=ProvisionerClusteringAttributes()
      attrs={}
      i=0
      for k in p.attributes.keys():
         attrs[k] = self.attr_vals[i]
         i = i+1
      return attrs


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

class ProvisionerK8SCluster(ProvisionerCluster):
   def __init__(self, key, attr_vals, pod_attrs, max_wait_onerror=1000):
      ProvisionerCluster.__init__(self, key, attr_vals)
      self.pod_attrs = pod_attrs
      self.max_wait_onerror=max_wait_onerror  # in seconds

   def count_states(self, max_wait_onerror=None):
      "Returns (waiting,unmatched,claimed,failed,unknown) counts"
      waiting_cnt = 0
      unmatched_cnt = 0
      claimed_cnt = 0
      failed_cnt = 0
      unknown_cnt = 0

      if max_wait_onerror==None:
         max_wait_onerror=self.max_wait_onerror

      err_deadline = datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(seconds=max_wait_onerror)
      for el in self.elements:
         pod_el = el[0]
         phase="%s"%pod_el['Phase']
         if phase=="Running":
            startd_el = el[1]
            if startd_el!=None:
              state = "%s"%startd_el['State']
            else:
              state = "None"
            # we will count all Running pods that are not yet claimed
            if state=="None":
              waiting_cnt+=1
            elif state!="Claimed":
              unmatched_cnt+=1
            else:
              claimed_cnt+=1
         elif phase=="Pending":
            # we can safely count these as waiting at all times
            waiting_cnt+=1
         elif (phase=="Succeeded"):
            # we can safely ignore these
            pass
         elif (phase=="Failed"):
            if pod_el['HasContainers']:
               failed_cnt+=1
            else:
               unknown_cnt+=1
         else:
            unknown_cnt+=1
            # All other states should be transitory
            # if not, they are problematic and should be ignored
            err_time = None
            try:
               err_time=pod_el['StartTime']
            except:
               pass
            if (err_time==None):
               # no good estimate, just count as waiting
               waiting_cnt+=1
               unknown_cnt-=1
            elif err_time>err_deadline:
               # assume it is transitory, count as waiting
               waiting_cnt+=1
               unknown_cnt-=1
            #else, this is unlikely to recover, count as unknown
      return (waiting_cnt,unmatched_cnt,claimed_cnt,failed_cnt,unknown_cnt)

   def count_unclaimed(self, max_wait_onerror=None):
      (waiting_cnt,unmatched_cnt,claimed_cnt,failed_cnt,unknown_cnt)=self.count_states(max_wait_onerror)
      # "logically unclaimed" = waiting+"running unmatched"
      return waiting_cnt+unmatched_cnt

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

            sval="%s"%val
            if sval=="Undefined":
               val = self.attrs.attributes[k]
               sval="%s"%val

            job_attrs.append(sval)
            key_attrs[jobk]=val
            del sval
            del val
         job_key=";".join(job_attrs)
         if job_key not in clusters:
            clusters[job_key] = ProvisionerScheddCluster(job_key, job_attrs, key_attrs)
         clusters[job_key].append(job)
         # cleanup to avoid accidental reuse
         del job_attrs
         del key_attrs

      return clusters


   def cluster_k8s_pods(self, k8s_pods, startd_ads):
      startd_dict={}
      for ad in startd_ads:
         k=ad["K8SPodName"]
         startd_dict[k]=ad
         del k

      clusters={}
      for pod in k8s_pods:
         if pod['Name'] in startd_dict:
           pod_ad = startd_dict[pod['Name'] ]
         else:
           pod_ad = None
         pod_attrs=[]
         key_attrs={}
         for k in self.attrs.attributes.keys():
            podk = self.attrs.expand_k8s_attr(k)
            if podk in pod.keys():
               val = pod[podk]
            else:
               val = self.attrs.attributes[k]
            pod_attrs.append("%s"%val)
            key_attrs[podk]=val
         pod_key=";".join(pod_attrs)
         if pod_key not in clusters:
            clusters[pod_key] = ProvisionerK8SCluster(pod_key, pod_attrs, key_attrs)
         clusters[pod_key].append( (pod,pod_ad) )
         # cleanup to avoid accidental reuse
         del pod_attrs
         del key_attrs
         del pod_ad

      return clusters

 
