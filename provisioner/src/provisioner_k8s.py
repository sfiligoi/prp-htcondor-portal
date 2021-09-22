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

   def query(self):
      """Return the list of jobs for my namespace"""

      pods=[]

      k8s = kubernetes.client.CoreV1Api()
      plist = k8s.list_namespaced_pod(namespace=self.namespace,
                                     label_selector="prp-htcondor-portal=wn")
      # TBD: We may need to check for continuation flag
      self._append_pods(pods,plist.items)

      return pods

   def create_job(self):
      condor_host = "prp-cm-htcondor.htcondor-portal.svc.cluster.local"

      labels = {
                 'k8s-app': 'prp-wn',
                 'prp-htcondor-portal': 'wn',
                 'PodCPUs': '1',
                 'PodGPUs': '1',
                 'PodMemory': '4096'
               }
      req = {
               'memory': '4096Mi',
               'cpu': 2,
               'nvidia.com/gpu': 1
            }
      env = [{'name': 'NUM_CPUS', 'value': '2'},
             {'name': 'NUM_GPUS', 'value': '1'},
             {'name': 'MEMORY', 'value': '4096'}]
      env.append({'name': 'K8S_NAMESPACE', 'value': self.namespace})
      env.append({'name': 'STARTD_NOCLAIM_SHUTDOWN', 'value': '1200'})
      env.append({'name': 'CONDOR_HOST', 'value': condor_host})
                  

      body = {
         'apiVersion': 'batch/v1',
         'kind': 'Job',
         'metadata': {
            'name': 'prp-wn-2', #TBD
            'namespace': self.namespace,
            'labels': labels
         },
         'spec': {
            'template': {
               'metadata': {
                  'labels': labels
               },
               'spec': {
                  'restartPolicy': 'Never',
                  'containers': [{
                     'name': 'htcondor',
                     'image': 'sfiligoi/prp-portal-wn',
                     'env': env,
                     'resources': {
                        'limits': req,
                        'requests': req
                     },
                     'volumeMounts': [{
                        'name': 'configpasswd',
                        'mountPath': '/etc/condor/tokens.d/prp-wn.token',
                        'subPath': 'prp-wn.token',
                        'readOnly': True
                      }]
                  }],
                  'volumes': [{
                     'name': 'configpasswd',
                     'secret': {
                        'secretName': 'prp-htcondor-wn-secret',
                        'items': [{
                           'key': 'prp-wn.token',
                           'path': 'prp-wn.token',
                           'defaultMode': 256
                        }]
                     }
                  }]
               }
            }
         }
      }

      k8s = kubernetes.client.BatchV1Api()
      k8s.create_namespaced_job(body=body, namespace=self.namespace)



   # INTERNAL
   def _append_pods(self, pods, mypods):
      """pods is a list and will be updated in-place"""
      for pod in mypods:
         podattrs={}
         labels=pod.metadata.labels
         for k in labels.keys():
            # convert all values to strings, for easier management
            podattrs[k]="%s"%labels[k]
         del labels
         podattrs['Name'] = pod.metadata.name
         podattrs['Namespace'] = pod.metadata.namespace
         podattrs['Phase'] = pod.status.phase
         pods.append(podattrs)
      return

