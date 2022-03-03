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
   fconfig = configparser.ConfigParser()
   fconfig.read(config_fname)
   kconfig = provisioner_k8s.ProvisionerK8SConfig(namespace=namespace, condor_host=condor_host)
   kconfig.parse(fconfig['k8s'])
   cconfig = provisioner_htcondor.ProvisionerHTCConfig(namespace=namespace, condor_host=condor_host)
   cconfig.parse(fconfig['htcondor'])
   log_obj = provisioner_logging.ProvisionerStdoutLogging(want_log_debug=True)
   # TBD: Proper security
   schedd_obj = provisioner_htcondor.ProvisionerSchedd({'.*':'.*'}), cconfig
   collector_obj = provisioner_htcondor.ProvisionerCollector('.*', cconfig)
   k8s_obj = provisioner_k8s.ProvisionerK8S(kconfig)
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

