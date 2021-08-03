#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi 2021
#
# Implement the event loop
#

class ProvisionerEventLoop:
   def __init__(self, schedd_obj, k8s_obj):
      self.schedd = schedd_obj
      self.k8s = k8s_obj

   def one_iteration(self):
      condor_clusters = self.schedd.query_idle()
      k8s_clusters = self.k8s.query()

      all_clusters_set = set(condor_clusters.keys())|set(k8s_clusters.keys())
      for ckey in all_clusters_set:
         if ckey in condor_clusters:
             self._one_cluster(ckey, condor_clusters[ckey], k8s_clusters[ckey] if ckey in k8s_clusters else None )
         else:
            # we have k8s cluster, but no condor jobs
            pass # noop for now, may eventually do something

       # explicit cleanup to avoid accidental reuse 
       del all_clusters_set
       del condor_clusters
       del k8s_clusters


   # INTERNAL

   def _one_cluster(self, cluster_id, condor_cluster, k8s_cluster):
      # TBD
      return
