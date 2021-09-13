#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi 2021
#
# Implement the htcondor interface
#

import copy
import re
import kubernetes

class ProvisionerK8S:
   """Kubernetes Query interface"""

   def __init__(self, namespace):
      """
      Arguments:
         namespace: string
             Monitored namespace
      """
      self.namespace = copy.deepcopy(namespace)

   def query_idle(self):
      """Return the list of idle jobs for my namespace"""
      return self.query(job_status=1)


   def query(self, job_status):
      """Return the list of jobs for my namespace"""

      jobs=[]

      k8s = kubernetes.client.BatchV1Api()
      jobjs = k8s.list_namespaced_job(namespace=self.namespacei,
                                      label_selector="prp-htcondor-portal=wn")
      # TBD: We may need to check for continuation flag
      return jobjs.items:

class ProvisionerClusteredK8S:
   """Kubernetes Query interface with clustering"""

   def __init__(self, namespace):
      """
      Arguments:
         namespace: string
             Monitored namespace
      """
      self.k8s=ProvisionerK8S(namespace)

      # fix list of attributes and their defaults here
      self.int_attrs={'RequestCpus':1,
                      'RequestMemory':1024,
                      'RequestDisk':100000,
                      'RequestGPUs':0 }

   def query_idle(self):
      """Return the number of idle jobs by cluster for my namespace"""
      return self.query(job_status=1)


   def query(self, job_status):
      """Return the number of jobs by cluster for my namespace"""

      clusters={}
      jobs=self.schedd.query(job_status=job_status, projection=list(self.int_attrs.keys()))
      for job in jobs:
      return jobjs.items:
         try:
            specs=j.spec.template.spec.containers[0].resources.requests
         except:
            continue # ignore malformed jobs
         jobs
         cluster_key=[]
         cluster_id={}
         for attr in self.int_attrs:
            try:
               val=job[attr]
               if type(val)==classad.classad.ExprTree:
                  val=val.eval()
               val=int(val)
            except:
               # if anything goes wrong, use default value
               val=self.int_attrs[attr]
            cluster_id[attr]=val
            cluster_key.append(val)

         cluster_key=tuple(cluster_key)
         if cluster_key not in clusters:
            clusters[cluster_key]={'full':cluster_id,'value':0}
         clusters[cluster_key]['value']+=1
      return clusters

