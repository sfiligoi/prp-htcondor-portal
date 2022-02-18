#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi 2021
#
# Main entry point of the provisioner process
#

import sys
import time
import configparser

from . import provisioner_logging
from . import provisioner_htcondor
from . import provisioner_k8s
from . import event_loop


def main(config_fname, namespace, condor_host, max_pods_per_cluster=10, sleep_time=10):
   config = configparser.ConfigParser()
   config.read(config_fname)
   config['k8s']['condor_host'] = condor_host
   log_obj = provisioner_logging.ProvisionerStdoutLogging(want_log_debug=True)
   # TBD: Proper security
   schedd_obj = provisioner_htcondor.ProvisionerSchedd(namespace, {'.*':'.*'})
   collector_obj = provisioner_htcondor.ProvisionerCollector(namespace, '.*')
   k8s_obj = provisioner_k8s.ProvisionerK8S(namespace, config['k8s'])
   k8s_obj.authenticate()

   el = event_loop.ProvisionerEventLoop(log_obj, schedd_obj, collector_obj, k8s_obj, max_pods_per_cluster)
   while True:
      log_obj.log_debug("[Main] Iteration started")
      try:
         el.one_iteration()
      except:
         log_obj.log_debug("[Main] Exception in one_iteration")
      log_obj.sync()
      time.sleep(sleep_time)

if __name__ == "__main__":
   # execute only if run as a script
   main(sys.argv[1], sya.argv[2], sys.argv[3])

