#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi@UCSD 2021
#
# Implement the Kubernetes interface
#

import copy
import re
import kubernetes
import time

class ProvisionerK8S:
   """Kubernetes Query interface"""

   def __init__(self, namespace,
                condor_host="prp-cm-htcondor.htcondor-portal.svc.cluster.local",
                k8s_image='sfiligoi/prp-portal-wn',
                k8s_image_pull_policy='Always',
                priority_class = None,
                base_tolerations = [],
                additional_labels = {},
                additional_envs = [],
                additional_volumes = {},
                additional_tolerations = [],
                additional_node_selectors = {}):
      """
      Arguments:
         namespace: string
             Monitored namespace
         condor_host: string (Optional)
             DNS address of the HTCOndor collector
         k8s_image: string (Optional)
             WN Container image to use in the pod
         k8s_image_pull_policy: string (Optional)
             WN Container image pull policy
         priority_class: string (Optional)
             priorityClassName to associate with the pod
         base_tolerations: list of strings (Optional)
             Tolerations of the form NoSchedule/Exists to add to the container
         additional_labels: dictionary of strings (Optional)
             Labels to attach to the pod
         additional_envs: list of (name,value) pairs (Optional)
             Environment values to add to the container
         additional_volumes: dictionary of (volume,mount) pairs (Optional)
             Volumes to mount in the pod. Both volume and mount must be a dictionary.
         additional_tolerations: list of dictionaries (Optional)
             Tolerations to add to the container
         additional_node_selectors: dictionary of strings (Optional)
             nodeSelectors to attach to the pod
      """
      self.start_time = int(time.time())
      self.app_name = 'prp-wn'
      self.submitted = 0
      # use deepcopy to avoid surprising changes at runtime
      self.namespace = copy.deepcopy(namespace)
      self.condor_host = copy.deepcopy(condor_host)
      self.k8s_image = copy.deepcopy(k8s_image)
      self.k8s_image_pull_policy = copy.deepcopy(k8s_image_pull_policy)
      self.priority_class = copy.deepcopy(priority_class)
      self.base_tolerations = copy.deepcopy(base_tolerations)
      self.additional_labels = copy.deepcopy(additional_labels)
      self.additional_envs = copy.deepcopy(additional_envs)
      self.additional_volumes = copy.deepcopy(additional_volumes)
      self.additional_tolerations = copy.deepcopy(additional_tolerations)
      self.additional_node_selectors = additional_node_selectors
      return

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
                 'k8s-app': self.app_name,
                 'prp-htcondor-portal': 'wn',
                 'PodCPUs':   "%i"%int_vals['CPUs'],
                 'PodGPUs':   "%i"%int_vals['GPUs'],
                 'PodMemory': "%i"%int_vals['Memory']
               }
      for k in self.additional_labels.keys():
         labels[k] = copy.copy(self.additional_labels[k])
      self._augment_labels(labels, attrs)

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
                   ('MEMORY',   "%i"%int_vals['Memory'])] + \
                 self.additional_envs
      self._augment_environment(env_list, attrs)

      # bosy will need it in list/dict form
      env = []
      for el in env_list:
         env.append({'name': el[0], 'value': el[1]})

      # no other defaults, so just start with the additional ones
      volumes_raw = copy.deepcopy(self.additional_volumes)
      self._augment_volumes(volumes_raw, attrs)

      pod_volumes = []
      mounts = []
      for k in volumes_raw.keys():
         el = volumes_raw[k]
         el_new = copy.copy(el[0])
         el_new['name']=k
         pod_volumes.append(el_new)

         el_new = copy.copy(el[1])
         el_new['name']=k
         mounts.append(el_new)

         # avoid accidental reuse
         del el_new

      # no other defaults, so just start with the additional ones
      tolerations = copy.deepcopy(self.additional_tolerations)
      self._augment_tolerations(tolerations, attrs)

      # no other defaults, so just start with the additional ones
      node_selectors = copy.deepcopy(self.additional_node_selectors)
      self._augment_node_selectors(node_selectors, attrs)

      k8s_image,k8s_image_pull_policy = self._get_k8s_image(attrs)
      priority_class = self._get_priority_class(attrs)

      job_name = '%s-%x-%06x'%(self.app_name,self.start_time,self.submitted)
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
                  'tolerations' : tolerations,
                  'nodeSelector' : node_selectors,
                  'containers': [{
                     'name': 'htcondor',
                     'image': k8s_image,
                     'imagePullPolicy': k8s_image_pull_policy,
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

      if priority_class!=None:
         body['spec']['template']['spec']['priorityClassName'] = priority_class

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
   def _get_k8s_image(self, attrs):
      return (self.k8s_image,self.k8s_image_pull_policy)

   def _get_priority_class(self, attrs):
      return self.priority_class

   def _augment_labels(self, labels, attrs):
      """Add any additional labels to the dictionary (attrs is read-only)"""
      return

   def _augment_environment(self, env_list, attrs):
      """Add any additional (name,value) pairs to the list (attrs is read-only)"""
      return

   def _augment_volumes(self, volumes, attrs):
      """Add any additional (volume,mount) pair to the dictionary (attrs is read-only)"""

      # by default, we mount the token secret
      volumes['configpasswd'] = \
                   (
                      {
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
                         'mountPath': '/etc/condor/tokens.d/prp-wn.token',
                         'subPath': 'prp-wn.token',
                         'readOnly': True
                      }
                   )

      return

   def _augment_tolerations(self, t_list, attrs):
      """Add any additional dictionaries to the list (attrs is read-only)"""
      for t in self.base_tolerations:
         t_list.append({'effect': 'NoSchedule',
                        'key': t,
                        'operator': 'Exists'})

      return

   def _augment_node_selectors(self, node_selectors, attrs):
      """Add any additional elements to the dictionary (attrs is read-only)"""
      return

