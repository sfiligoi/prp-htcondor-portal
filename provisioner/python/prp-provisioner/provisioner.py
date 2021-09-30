#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi 2021
#
# Main entry point of the provisioner process
#

import sys
import time

import provisioner_logging
import provisioner_htcondor
import provisioner_k8s
import event_loop

def main(namespace, max_pods_per_cluster=10, sleep_time=10):
   log_obj = provisioner_logging.ProvisionerStdoutLogging(want_log_debug=True)
   # TBD: Proper security
   schedd_obj = provisioner_htcondor.ProvisionerSchedd(namespace, {'.*':'.*'})
   collector_obj = provisioner_htcondor.ProvisionerCollector(namespace, '.*')
   k8s_obj = provisioner_k8s.ProvisionerK8S(namespace)
   k8s_obj.authenticate()

   el = event_loop.ProvisionerEventLoop(log_obj, schedd_obj, collector_obj, k8s_obj, max_pods_per_cluster)
   while True:
      log_obj.log_debug("[Main] Iteration started")
      try:
         el.one_iteration()
      except:
         log_obj.log_debug("[Main] Exception in one_iteration")
      time.sleep(sleep_time)

if __name__ == "__main__":
   # execute only if run as a script
   main(sys.argv[1])

