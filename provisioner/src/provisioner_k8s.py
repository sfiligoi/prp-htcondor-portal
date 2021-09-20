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

   def authenticate(self, use_service_account=True):
      """Load credentials needed for authentication"""
      if use_service_account:
         # The pod must have a service accoun associated with it
         # https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
         # It also relies on KUBERNETES_SERVICE_HOST and KUBERNETES_SERVICE_PORT beign set
         kubernetes.config.load_incluster_config()
      else:
         # Read config from ~/.kube/config
         kubernetes.config.load_kube_config()

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


