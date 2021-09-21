#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi 2021
#
# Implement the event loop
#

class ProvisionerEventLoop:
   def __init__(self, log_obj, schedd_obj, collector_obj, k8s_obj, max_pods_per_cluster):
      self.log_obj = log_obj
      self.schedd = schedd_obj
      self.collector = collector_obj
      self.k8s = k8s_obj
      self.max_pods_per_cluster = max_pods_per_cluster

   def one_iteration(self):
      schedd_jobs = self.schedd.query_idle()
      startd_pods = self.collector.query_startds()
      k8s_pods = self.k8s.query_unclaimed(startd_pods)

      del startd_pods

      clustering = ProvisionerClustering()
      schedd_clusters = clustering.cluster_schedd_jobs(schedd_jobs)
      k8s_clusters = clustering.cluster_k8s_pods(k8s_pods)

      del schedd_jobs
      del k8s_pods

      all_clusters_set = set(schedd_clusters.keys())|set(k8s_clusters.keys())
      for ckey in all_clusters_set:
         try:
            if ckey in schedd_clusters:
               self._provision_cluster(ckey, schedd_clusters[ckey], k8s_clusters[ckey] if ckey in k8s_clusters else None )
            else:
               # we have k8s cluster, but no condor jobs
               pass # noop for now, may eventually do something
         except:
            log.debug("[ProvisionerEventLoop] Exception in cluster  %s"%ckey)

       # explicit cleanup to avoid accidental reuse 
       del all_clusters_set
       del schedd_clusters
       del k8s_clusters


   # INTERNAL
   def _cluster_jobs(schedd_jobs):
      for job in schedd_jobs:


   def _provision_cluster(self, cluster_id, schedd_cluster, k8s_cluster):
      "Check if we have enough k8s clusters. Submit more if needed"
      n_jobs_idle = schedd_cluster.count_idle()
      if n_jobs_idle==0:
         self.log_obj.log_debug("ProvisionerEventLoop] Cluster %s n_jobs_idle==0 found!"%cluster_id)
         return # should never get in here, but just in case (nothing to do, we are done)

      # assume some latency and pod reuse
      min_pods = 1 + (n_jobs_idle/4)
      if min_pods>20:
         # when we have a lot of jobs, slow futher
         min_pods = 20 + (min_pods-20)/4

      if min_pods>self.max_pods_per_cluster:
         min_pods = self.max_pods_per_cluster

      n_pods_unclaimed = k8s_cluster.count_unclaimed()
      self.log_obj.log_debug("ProvisionerEventLoop] Cluster %s n_jobs_idle %i n_pods_unclaimed %i min_pods %i"%
                             (cluster_id, n_jobs_idle, n_pods_unclaimed, min_pods)
      if n_pods_unclaimed>=min_pods:
         pass # we have enough pods, do nothing for now
         # we may want to do some sanity checks here, eventually
      else:
         self.k8s.submit(k8s_cluster, min_pods-n_pods_unclaimed)

      return
