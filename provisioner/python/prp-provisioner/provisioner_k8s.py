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
import time

class ProvisionerK8S:
   """Kubernetes Query interface"""

   def __init__(self, namespace,
                condor_host="prp-cm-htcondor.htcondor-portal.svc.cluster.local",
                k8s_image='sfiligoi/prp-portal-wn'):
      """
      Arguments:
         namespace: string
             Monitored namespace
      """
      self.namespace = copy.deepcopy(namespace)
      self.condor_host = condor_host
      self.k8s_image = k8s_image
      self.start_time = int(time.time())
      self.submitted = 0

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

   def submit(self, attrs, n_pods=1):
      # first ensure that the basic int values are valid
      int_vals={}
      for k in ('CPUs','GPUs','Memory'):
         int_vals[k] = int(attrs[k])

      labels = {
                 'k8s-app': 'prp-wn',
                 'prp-htcondor-portal': 'wn',
                 'PodCPUs':   "%i"%int_vals['CPUs'],
                 'PodGPUs':   "%i"%int_vals['GPUs'],
                 'PodMemory': "%i"%int_vals['Memory']
               }
      self._augment_labels(labels)

      req = {
               'memory':  '%iMi'%int_vals['Memory'],
               'cpu':            int_vals['CPUs'],
               'nvidia.com/gpu': int_vals['GPUs']
            }
      env_list = [ ('CONDOR_HOST', self.condor_host),
                   ('STARTD_NOCLAIM_SHUTDOWN', '1200'),
                   ('K8S_NAMESPACE', self.namespace),
                   ('NUM_CPUS', "%i"%int_vals['CPUs']),
                   ('NUM_GPUS', "%i"%int_vals['GPUs']),
                   ('MEMORY',   "%i"%int_vals['Memory'])]
      self._augment_environment(env_list)

      # bosy will need it in list/dict form
      env = []
      for el in env_list:
         env.append({'name': el[0], 'value': el[1]})

      volumes_list = []
      self._augment_volumes(volumes_list)

      pod_volumes = []
      mounts = []
      for el in volumes_list:
         pod_volumes.append(el[0])
         mounts.append(el[1])

      job_name = 'prp-wn-%x-%03x'%(self.start_time,self.submitted)
      self.submitted = self.submitted + 1

      body = {
         'apiVersion': 'batch/v1',
         'kind': 'Job',
         'metadata': {
            'name': job_name,
            'namespace': self.namespace,
            'labels': labels
         },
         'spec': {
            'parallelism': n_pods,
            'completions': n_pods,
            'template': {
               'metadata': {
                  'labels': labels
               },
               'spec': {
                  'restartPolicy': 'Never',
                  'containers': [{
                     'name': 'htcondor',
                     'image': self.k8s_image,
                     'env': env,
                     'resources': {
                        'limits': req,
                        'requests': req
                     },
                     'volumeMounts': mounts,
                  }],
                  'volumes': pod_volumes
               }
            }
         }
      }

      k8s = kubernetes.client.BatchV1Api()
      k8s.create_namespaced_job(body=body, namespace=self.namespace)

      return job_name


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
         podattrs['Phase'] = pod.status.phase
         pods.append(podattrs)
      return

   # These can be re-implemented by derivative classes
   def _augment_labels(self, labels):
      """Add any additional labels to the dictionary"""
      return

   def _augment_environment(self, env_list):
      ""Add any additional (value, key) pairs to the list"""
      return

   def _augment_volumes(self, volumes):
      ""Add any additional (volume,mount) pairs to the list"""

      # by default, we mount the token secret
      volumes.append(({
                         'name': 'configpasswd',
                         'secret': {
                            'secretName': 'prp-htcondor-wn-secret',
                            'items': [{
                               'key': 'prp-wn.token',
                               'path': 'prp-wn.token',
                               'defaultMode': 256
                            }]
                         }
                      },
                      {
                         'name': 'configpasswd',
                         'mountPath': '/etc/condor/tokens.d/prp-wn.token',
                         'subPath': 'prp-wn.token',
                         'readOnly': True
                      }))

      return

