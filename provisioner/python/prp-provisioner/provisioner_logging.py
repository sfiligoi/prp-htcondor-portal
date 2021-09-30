#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi 2021
#

import time

# abstract class, missing log method
class ProvisionerBaseLogging:
   def __init__(self, want_log_debug=False, want_log_info=True):
      self.want_log_debug = want_log_debug
      self.want_log_info  = want_log_info

   def log_info(self, message):
      if self.want_log_info:
         self.log("INFO", message)

   def log_error(self, message):
      self.log("ERROR", message)

   def log_debug(self, message):
      if self.want_log_debug:
         self.log("DEBUG", message)

class ProvisionerStdoutLogging(ProvisionerBaseLogging):
   def __init__(self, want_log_debug=False, want_log_info=True):
      ProvisionerBaseLogging.__init__(self, want_log_debug, want_log_info)

   def log(self, level_str, message):
      now = time.ctime()
      print("%s [%s] %s"%(now, level_str, message) )

