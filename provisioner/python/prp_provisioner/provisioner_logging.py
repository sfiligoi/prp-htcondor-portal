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

   # logs are not guaranteed to be saved until sync is called
   def sync(self):
      return #derivative classes can update this

class ProvisionerStdoutLogging(ProvisionerBaseLogging):
   def __init__(self, want_log_debug=False, want_log_info=True):
      ProvisionerBaseLogging.__init__(self, want_log_debug, want_log_info)

   def log(self, level_str, message):
      now = time.ctime()
      print("%s [%s] %s"%(now, level_str, message) )


class ProvisionerFileLogging(ProvisionerBaseLogging):
   def __init__(self, fname, dated=True, want_log_debug=False, want_log_info=True):
      ProvisionerBaseLogging.__init__(self, want_log_debug, want_log_info)
      self.buffer = []
      self.fname = fname
      self.dated = dated

   def log(self, level_str, message):
      now = time.ctime()
      self.buffer.append("%s [%s] %s\n"%(now, level_str, message) )

   def sync(self):
      if len(self.buffer)==0:
         return # nothing to do
      fname = self._getfname()
      blob = "".join(self.buffer);
      with open(fname,"a") as fd:
         fd.write(blob);
      # we can now reset the buffer
      self.buffer = []

   # internal
   def _getfname(self):
      if self.dated:
          return "%s.%s"%(self.fname,time.strftime("%Y%m%d"))
      else:
          return self.fname



