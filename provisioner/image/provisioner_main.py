#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi 2022
#
# Main entry point of the provisioner process
#

import sys
import time
import configparser

import prp_provisioner.provisioner_k8s as provisioner_k8s
import prp_provisioner.provisioner_logging as provisioner_logging
import prp_provisioner.provisioner_htcondor as provisioner_htcondor
import prp_provisioner.event_loop as event_loop

def main(log_fname, namespace, max_pods_per_cluster=20, sleep_time=60):
   fconfig = configparser.ConfigParser()
   fconfig.read(('pod.conf','osg_provisioner.conf'))
   kconfig = provisioner_k8s.ProvisionerK8SConfig(namespace)
   cconfig = provisioner_htcondor.ProvisionerHTCConfig(namespace)

   if 'k8s' in fconfig:
      kconfig.parse(fconfig['k8s'])
   else:
      kconfig.parse(fconfig['DEFAULT'])

   if 'htcondor' in fconfig:
      cconfig.parse(fconfig['htcondor'])
   else:
      cconfig.parse(fconfig['DEFAULT'])

   log_obj = provisioner_logging.ProvisionerFileLogging(log_fname, want_log_debug=True)
   # TBD: Strong security
   schedd_obj = provisioner_htcondor.ProvisionerSchedd({'.*':'.*'}, cconfig)
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
   main(sys.argv[1], sys.argv[2])

