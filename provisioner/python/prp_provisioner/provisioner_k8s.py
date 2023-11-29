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

from . import provisioner_config_parser

ProvisionerK8SConfigFields = ('namespace','condor_host',
                              'k8s_image','k8s_image_pull_policy',
                              'priority_class','priority_class_cpu','priority_class_gpu',
                              'tolerations_list', 'node_selectors_dict', 'node_affinity_dict',
                              'labels_dict', 'annotations_dict', 'envs_dict',
                              'pvc_volumes_dict', 'config_volumes_dict',
                              'app_name','k8s_job_ttl','k8s_domain',
                              'force_k8s_namespace_matching',
                              'request_fuse','storage_mbs','resources_dict',
                              'additional_requirements',
                              'use_large_limit')

class ProvisionerK8SConfig:
   """Config fie for ProvisionerK8S"""

   def __init__(self, namespace,
                condor_host="prp-cm-htcondor.htcondor-portal.svc.cluster.local",
                k8s_image='sfiligoi/prp-portal-wn',
                k8s_image_pull_policy='Always',
                priority_class = None,
                priority_class_cpu = None,
                priority_class_gpu = None,
                base_tolerations = [],
                base_pvc_volumes = {},
                additional_labels = {},
                additional_envs = {},
                additional_volumes = {},
                additional_tolerations = [],
                additional_node_selectors = {},
                additional_annotations = {},
                app_name = 'prp-wn',
                k8s_job_ttl = 24*3600, # clean after 1 day
                k8s_domain = 'optiputer.net',
                force_k8s_namespace_matching = "yes",
                additional_requirements = "",
                node_affinity_dict = {}):
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
         priority_class_cpu: string (Optional)
             priorityClassName to associate with CPU pod
         priority_class_cpu: string (Optional)
             priorityClassName to associate with GPU pod
         base_tolerations: list of strings (Optional)
             Tolerations of the form NoSchedule/Exists to add to the container
         base_pvc_volumes: list of strings (Optional)
             PersistentVolumeClaims to add to the container, vvalues is mountpoint
         additional_labels: dictionary of strings (Optional)
             Labels to attach to the pod
         additional_envs: dictionary of strings (Optional)
             Environment values to add to the container
         additional_volumes: dictionary of (volume,mount) pairs (Optional)
             Volumes to mount in the pod. Both volume and mount must be a dictionary.
         additional_tolerations: list of dictionaries (Optional)
             Tolerations to add to the container
         additional_node_selectors: dictionary of strings (Optional)
             nodeSelectors to attach to the pod
         additional_annotations: dictionary of strings (Optional)
             Annotations to attach to the pod
         k8s_domain: string (Optional)
             Kubernetes domain to advertise
         node_affinity_dict: dictionary of node affinity (Optional)
             If key is prepended with ^, NotIn is used (In else)
             Each value is either a tuple of strings
             or a | separated string
      """
      self.namespace = copy.deepcopy(namespace)
      self.condor_host = copy.deepcopy(condor_host)
      self.k8s_image = copy.deepcopy(k8s_image)
      self.k8s_image_pull_policy = copy.deepcopy(k8s_image_pull_policy)
      self.priority_class = copy.deepcopy(priority_class)
      self.priority_class_cpu = copy.deepcopy(priority_class_cpu)
      self.priority_class_gpu = copy.deepcopy(priority_class_gpu)
      self.base_tolerations = copy.deepcopy(base_tolerations)
      self.base_pvc_volumes = copy.deepcopy(base_pvc_volumes)
      self.base_config_volumes = {}
      self.additional_labels = copy.deepcopy(additional_labels)
      self.additional_envs = copy.deepcopy(additional_envs)
      self.additional_volumes = copy.deepcopy(additional_volumes)
      self.additional_tolerations = copy.deepcopy(additional_tolerations)
      self.additional_node_selectors = additional_node_selectors
      self.additional_annotations = copy.deepcopy(additional_annotations)
      self.app_name = copy.deepcopy(app_name)
      self.k8s_job_ttl = k8s_job_ttl
      self.k8s_domain = copy.deepcopy(k8s_domain)
      self.force_k8s_namespace_matching = copy.deepcopy(force_k8s_namespace_matching)
      self.additional_requirements = copy.deepcopy(additional_requirements)
      self.node_affinity_dict = copy.deepcopy(node_affinity_dict)
      self.request_fuse = "yes"
      self.storage_mbs = "20000"
      self.additional_resources = {}
      self.use_large_limit = "yes"

   def parse(self,
             dict,
             fields=ProvisionerK8SConfigFields):
      """Parse the valuies from a dictionary"""
      self.namespace = provisioner_config_parser.update_parse(self.namespace, 'namespace', 'str', fields, dict)
      self.condor_host = provisioner_config_parser.update_parse(self.condor_host, 'condor_host', 'str', fields, dict)
      self.k8s_domain = provisioner_config_parser.update_parse(self.k8s_domain, 'k8s_domain', 'str', fields, dict)
      self.k8s_image = provisioner_config_parser.update_parse(self.k8s_image, 'k8s_image', 'str', fields, dict)
      self.k8s_image_pull_policy = provisioner_config_parser.update_parse(self.k8s_image_pull_policy, 'k8s_image_pull_policy', 'str', fields, dict)
      self.priority_class = provisioner_config_parser.update_parse(self.priority_class, 'priority_class', 'str', fields, dict)
      self.priority_class_cpu = provisioner_config_parser.update_parse(self.priority_class_cpu, 'priority_class_cpu', 'str', fields, dict)
      self.priority_class_gpu = provisioner_config_parser.update_parse(self.priority_class_gpu, 'priority_class_gpu', 'str', fields, dict)
      self.base_tolerations = provisioner_config_parser.update_parse(self.base_tolerations, 'tolerations_list', 'list', fields, dict)
      self.base_pvc_volumes = provisioner_config_parser.update_parse(self.base_pvc_volumes, 'pvc_volumes_dict', 'dict', fields, dict)
      self.base_config_volumes = provisioner_config_parser.update_parse(self.base_config_volumes, 'config_volumes_dict', 'dict', fields, dict)
      self.additional_labels = provisioner_config_parser.update_parse(self.additional_labels, 'labels_dict', 'dict', fields, dict)
      self.additional_envs = provisioner_config_parser.update_parse(self.additional_envs, 'envs_dict', 'dict', fields, dict)
      self.additional_node_selectors = provisioner_config_parser.update_parse(self.additional_node_selectors, 'node_selectors_dict', 'dict', fields, dict)
      self.additional_annotations = provisioner_config_parser.update_parse(self.additional_annotations, 'annotations_dict', 'dict', fields, dict)
      self.app_name = provisioner_config_parser.update_parse(self.app_name, 'app_name', 'str', fields, dict)
      self.k8s_job_ttl = provisioner_config_parser.update_parse(self.k8s_job_ttl, 'k8s_job_ttl', 'int', fields, dict)
      self.force_k8s_namespace_matching = provisioner_config_parser.update_parse(self.force_k8s_namespace_matching, 'force_k8s_namespace_matching', 'str', fields, dict)
      self.additional_requirements = provisioner_config_parser.update_parse(self.additional_requirements, 'additional_requirements', 'str', fields, dict)
      self.node_affinity_dict = provisioner_config_parser.update_parse(self.node_affinity_dict, 'node_affinity_dict', 'dict', fields, dict)
      self.request_fuse = provisioner_config_parser.update_parse(self.request_fuse, 'request_fuse', 'str', fields, dict)
      self.storage_mbs = provisioner_config_parser.update_parse(self.storage_mbs, 'storage_mbs', 'str', fields, dict)
      self.additional_resources = provisioner_config_parser.update_parse(self.additional_resources, 'resources_dict', 'dict', fields, dict)
      self.use_large_limit = provisioner_config_parser.update_parse(self.use_large_limit, 'use_large_limit', 'str', fields, dict)

class ProvisionerK8S:
   """Kubernetes Query interface"""

   def __init__(self, config):
      self.start_time = int(time.time())
      self.submitted = 0
      # use deepcopy to avoid surprising changes at runtime
      self.app_name = copy.deepcopy(config.app_name)
      self.k8s_job_ttl = config.k8s_job_ttl
      self.namespace = copy.deepcopy(config.namespace)
      self.condor_host = copy.deepcopy(config.condor_host)
      self.k8s_image = copy.deepcopy(config.k8s_image)
      self.k8s_image_pull_policy = copy.deepcopy(config.k8s_image_pull_policy)
      self.priority_class = copy.deepcopy(config.priority_class)
      self.priority_class_cpu = copy.deepcopy(config.priority_class_cpu)
      self.priority_class_gpu = copy.deepcopy(config.priority_class_gpu)
      self.base_tolerations = copy.deepcopy(config.base_tolerations)
      self.base_pvc_volumes = copy.deepcopy(config.base_pvc_volumes)
      self.base_config_volumes = copy.deepcopy(config.base_config_volumes)
      self.additional_labels = copy.deepcopy(config.additional_labels)
      self.additional_envs = copy.deepcopy(config.additional_envs)
      self.additional_volumes = copy.deepcopy(config.additional_volumes)
      self.additional_tolerations = copy.deepcopy(config.additional_tolerations)
      self.additional_node_selectors = copy.deepcopy(config.additional_node_selectors)
      self.additional_annotations = copy.deepcopy(config.additional_annotations)
      self.k8s_domain = copy.deepcopy(config.k8s_domain)
      self.force_k8s_namespace_matching = copy.deepcopy(config.force_k8s_namespace_matching)
      self.additional_requirements = copy.deepcopy(config.additional_requirements)
      self.node_affinity_dict = copy.deepcopy(config.node_affinity_dict)
      self.request_fuse = copy.deepcopy(config.request_fuse)
      self.storage_mbs = copy.deepcopy(config.storage_mbs)
      self.additional_resources = copy.deepcopy(config.additional_resources)
      self.use_large_limit = copy.deepcopy(config.use_large_limit)
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
                                     label_selector="prp-htcondor-portal=wn,k8s-app=%s"%self.app_name)
      # TBD: We may need to check for continuation flag
      self._append_pods(pods,plist.items)

      return pods

   def submit(self, attrs, n_pods=1):
      # first ensure that the basic int values are valid
      int_vals={}
      for k in ('CPUs','GPUs','Memory','Disk'):
         int_vals[k] = int(attrs[k])

      labels = {
                 'k8s-app': self.app_name,
                 'prp-htcondor-portal': 'wn',
                 'PodCPUs':   "%i"%int_vals['CPUs'],
                 'PodGPUs':   "%i"%int_vals['GPUs'],
                 'PodMemory': "%i"%int_vals['Memory'],
                 'PodDisk': "%i"%int_vals['Disk']
               }
      for k in self.additional_labels.keys():
         labels[k] = copy.copy(self.additional_labels[k])
      self._augment_labels(labels, attrs)

      if self.use_large_limit == "yes":
         # CPU is hardly ever used 100%... request 75%
         # Similarly for memory, but request 80% there
         req = {
               'memory':  '%iMi'%int(int_vals['Memory']*0.8),
               'cpu':            (int_vals['CPUs']*0.75)
            }
         # but enforce Memory limit + delta
         lim = {
               'memory':  '%iMi'%(int_vals['Memory']+1000),
               'cpu':            (int_vals['CPUs']+0.25)
            }
      else:
         # Stick to the needs, with just small memory delta
         req = {
               'memory':  '%iMi'%(int_vals['Memory']+1000),
               'cpu':     int_vals['CPUs']
            }
         lim = {
               'memory':  '%iMi'%(int_vals['Memory']+1000),
               'cpu':     int_vals['CPUs']
            }

      if int_vals['GPUs']>0:
         req['nvidia.com/gpu'] = int_vals['GPUs']
         lim['nvidia.com/gpu'] = int_vals['GPUs']

      if self.request_fuse != "no":
         req['smarter-devices/fuse'] = "1"
         lim['smarter-devices/fuse'] = "1"

      if self.storage_mbs != "":
         # many jobs do not define reasonable Disk requests
         # keep a reasonable minimum
         min_disk = int(self.storage_mbs)*1024
         if int_vals['Disk']<min_disk:
            int_vals['Disk'] = min_disk

      req['ephemeral-storage'] = '%ik'%int_vals['Disk']
      lim['ephemeral-storage'] = '%ik'%int_vals['Disk']

      for k in self.additional_resources.keys():
         req[k] = copy.copy(self.additional_resources[k])
         lim[k] = copy.copy(self.additional_resources[k])

      env_list = [ ('K8S_PROVISIONER_TYPE', 'PRPHTCondorProvisioner'),
                   ('K8S_PROVISIONER_NAME', self.app_name),
                   ('CONDOR_HOST', self.condor_host),
                   ('STARTD_NOCLAIM_SHUTDOWN', '1200'),
                   ('K8S_NAMESPACE', self.namespace),
                   ('K8S_DOMAIN', self.k8s_domain),
                   ('NUM_CPUS', "%i"%int_vals['CPUs']),
                   ('NUM_GPUS', "%i"%int_vals['GPUs']),
                   ('MEMORY', "%i"%int_vals['Memory']),
                   ('DISK',   "%i"%int_vals['Disk'])]

      if self.force_k8s_namespace_matching != "":
         env_list.append(('FORCE_K8SNAMESPACE_MATCHING',self.force_k8s_namespace_matching))
      if self.additional_requirements != "" :
         env_list.append(('ADDITIONAL_REQUIREMENTS',self.additional_requirements))

      for k in self.additional_envs:
         env_list.append((k,self.additional_envs[k]))
      self._augment_environment(env_list, attrs)

      # bosy will need it in list/dict form
      env = []
      for el in env_list:
         env.append({'name': el[0], 'value': el[1]})

      # pass though the node we are running on
      nnobj=kubernetes.client.models.V1ObjectFieldSelector(field_path="spec.nodeName")
      nnenvsrc=kubernetes.client.models.V1EnvVarSource(field_ref=nnobj)
      nnenv=kubernetes.client.models.V1EnvVar(name='PHYSICAL_HOSTNAME', value='', value_from=nnenvsrc)
      env.append(nnenv)

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

      node_affinity_selectors = []
      for k in self.node_affinity_dict:
         if k[0]=='^':
            nstr=k[1:]
            ostr="NotIn"
         else:
            nstr=k
            ostr="In"
         val=self.node_affinity_dict[k]
         if type(val)==type(""):
            val=val.strip().split("|")
         node_affinity_selectors.append( {"key":nstr, "operator":ostr, 'values':val} )
         # avoid accidental reuse
         del nstr
         del ostr
         del val

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
            'ttlSecondsAfterFinished': self.k8s_job_ttl,
            'template': {
               'metadata': {
                  'labels': labels
               },
               'spec': {
                  'restartPolicy': 'Never',
                  'tolerations' : tolerations,
                  'nodeSelector' : node_selectors,
                  "affinity": {
                   "nodeAffinity": {
                    "requiredDuringSchedulingIgnoredDuringExecution": {
                     "nodeSelectorTerms": [ { "matchExpressions": node_affinity_selectors } ]
                    }
                   }
                  },
                  'containers': [{
                     'name': 'htcondor',
                     'image': k8s_image,
                     'imagePullPolicy': k8s_image_pull_policy,
                     'env': env,
                     'resources': {
                        'limits': lim,
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

      if len(self.additional_annotations.keys())!=0:
         # annotations are rare, so treat them explicitly here
         body['spec']['template']['metadata']['annotations'] = copy.deepcopy(self.additional_annotations)

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
         podattrs['StartTime'] = pod.status.start_time
         podattrs['HasContainers'] = pod.status.container_statuses!=None
         pods.append(podattrs)
      return

   # These can be re-implemented by derivative classes
   def _get_k8s_image(self, attrs):
      return (self.k8s_image,self.k8s_image_pull_policy)

   def _get_priority_class(self, attrs):
      if int(attrs['GPUs'])>0:
         pc = self.priority_class_gpu
      else:
         pc = self.priority_class_cpu
      if pc==None:
         pc = self.priority_class
      return pc

   def _augment_labels(self, labels, attrs):
      """Add any additional labels to the dictionary (attrs is read-only)"""
      return

   def _augment_environment(self, env_list, attrs):
      """Add any additional (name,value) pairs to the list (attrs is read-only)"""
      return

   def _augment_volumes(self, volumes, attrs):
      """Add any additional (volume,mount) pair to the dictionary (attrs is read-only)"""

      for v in self.base_pvc_volumes:
         # Special characters in the volume path
         #  ! - read only
         #  # - HostToContainer mountPropagation
         mro=False
         mhp=False
         mpath = self.base_pvc_volumes[v]
         while mpath[0] in ('!','#'):
            sc = mpath[0]
            mpath = mpath[1:]
            mro |= (sc=='!')
            mhp |= (sc=='#')

         vdict = {
                         'mountPath': mpath
                 }
         if mro:
            vdict['readOnly'] = True
         if mhp:
            vdict['mountPropagation'] = 'HostToContainer'

         volumes[v] = \
                   (
                      {
                         'persistentVolumeClaim': {
                            'claimName': v
                         }
                      },
                      vdict
                   )

      for v in self.base_config_volumes:
         path = self.base_config_volumes[v]
         fname = path.rsplit("/")[-1]
         volumes[v] = \
                   (
                      {
                         'configMap': {
                            'name': v,
                            'items': [{
                                'key': fname,
                                'path': fname
                            }]
                         }
                      },
                      {
                         'mountPath': path,
                         'subPath': fname
                      }
                   )


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

