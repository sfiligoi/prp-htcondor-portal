#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi 2021
#
# Implement the event loop
#

from . import provisioner_clustering

class ProvisionerEventLoop:
   def __init__(self, log_obj, schedd_obj, collector_obj, k8s_obj, max_pods_per_cluster, max_submit_pods_per_cluster):
      self.log_obj = log_obj
      self.schedd = schedd_obj
      self.collector = collector_obj
      self.k8s = k8s_obj
      self.max_pods_per_cluster = max_pods_per_cluster
      self.max_submit_pods_per_cluster = max_submit_pods_per_cluster

   def query_system(self):
      schedd_attrs = provisioner_clustering.ProvisionerClusteringAttributes().get_schedd_attributes()
      try:
         schedd_jobs = self.schedd.query_idle(projection=schedd_attrs)
         startd_pods = self.collector.query()
      except:
         self.log_obj.log_error("[ProvisionerEventQuery] Failed to query HTCondor")
         self.log_obj.sync()
         raise
      del schedd_attrs

      try:
         k8s_pods = self.k8s.query()
      except:
         self.log_obj.log_error("[ProvisionerEventQuery] Failed to query k8s")
         self.log_obj.sync()
         raise

      clustering = provisioner_clustering.ProvisionerClustering()
      schedd_clusters = clustering.cluster_schedd_jobs(schedd_jobs)
      k8s_clusters = clustering.cluster_k8s_pods(k8s_pods, startd_pods)

      return (schedd_clusters, k8s_clusters)

   def one_iteration(self):
      try:
        (schedd_clusters, k8s_clusters) = self.query_system()
      except:
         self.log_obj.log_error("[ProvisionerEventLoop] Failed to query")
         self.log_obj.sync()
         return

      all_clusters_set = set(schedd_clusters.keys())|set(k8s_clusters.keys())
      for ckey in all_clusters_set:
         try:
            k8s_cluster = k8s_clusters[ckey] if ckey in k8s_clusters else None
            if ckey in schedd_clusters:
               self._provision_cluster(ckey, schedd_clusters[ckey], k8s_cluster )
            else:
               # we have k8s cluster, but no condor jobs
               self._report_cluster(ckey, k8s_cluster)
         except:
            self.log_obj.log_debug("[ProvisionerEventLoop] Exception in cluster '%s'"%ckey)

      # explicit cleanup to avoid accidental reuse 
      del all_clusters_set
      del schedd_clusters
      del k8s_clusters

      self.log_obj.sync()


   # INTERNAL
   def _check_and_report_cluster(self, cluster_id, k8s_cluster, n_jobs_idle, min_pods):
      "Check if we have enough pods already, and also report"
      n_pods_statearr=k8s_cluster.count_states() if k8s_cluster!=None else (0,0,0,0,0)
      n_pods_waiting=n_pods_statearr[0]
      n_pods_unmatched=n_pods_statearr[1]
      n_pods_claimed=n_pods_statearr[2]
      n_pods_unclaimed = n_pods_waiting+n_pods_unmatched
      n_pods_total = n_pods_unclaimed+n_pods_claimed

      if n_pods_total>=self.max_submit_pods_per_cluster:
         min_pods = 0

      if (n_jobs_idle+n_pods_unclaimed+min_pods+n_pods_waiting+n_pods_unmatched+n_pods_claimed)>0:
        # do not report all zeros (e.g. only completed pods in the system)
        self.log_obj.log_debug("[ProvisionerEventLoop] Cluster '%s' n_jobs_idle %i n_pods_unclaimed %i min_pods %i (pods wait %i unmatched %i claimed %i max %i)"%
                               (cluster_id, n_jobs_idle, n_pods_unclaimed, min_pods, n_pods_waiting, n_pods_unmatched, n_pods_claimed, self.max_submit_pods_per_cluster))

      return (min_pods,n_pods_unclaimed)

   def _report_cluster(self, cluster_id, k8s_cluster):
      self._check_and_report_cluster(cluster_id, k8s_cluster, 0, 0)

   def _provision_cluster(self, cluster_id, schedd_cluster, k8s_cluster):
      "Check if we have enough k8s clusters. Submit more if needed"
      n_jobs_idle = schedd_cluster.count_idle()
      if n_jobs_idle==0:
         self.log_obj.log_debug("[ProvisionerEventLoop] Cluster '%s' n_jobs_idle==0 found!"%cluster_id)
         return # should never get in here, but just in case (nothing to do, we are done)

      # assume some latency and pod reuse
      min_pods = 1 + int(n_jobs_idle/4)
      if min_pods>20:
         # when we have a lot of jobs, slow futher
         min_pods = 20 + int((min_pods-20)/4)

      if min_pods>self.max_pods_per_cluster:
         min_pods = self.max_pods_per_cluster

      (min_pods,n_pods_unclaimed) = self._check_and_report_cluster(cluster_id, k8s_cluster, n_jobs_idle, min_pods)

      if n_pods_unclaimed>=min_pods:
         pass # we have enough pods, do nothing for now
         # we may want to do some sanity checks here, eventually
      else:
         try:
            job_name = self.k8s.submit(schedd_cluster.get_attr_dict(), min_pods-n_pods_unclaimed)
            self.log_obj.log_info("[ProvisionerEventLoop] Cluster '%s' Submitted %i pods as job %s"% 
                                  (cluster_id,min_pods-n_pods_unclaimed, job_name))
         except:
            self.log_obj.log_error("[ProvisionerEventLoop] Cluster '%s' Failed to submit %i pods"%
                                   (cluster_id,min_pods-n_pods_unclaimed))

      return

