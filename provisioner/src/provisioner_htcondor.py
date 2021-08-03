#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi 2021
#
# Implement the htcondor interface
#

import copy
import re
import htcondor

class ProvisionerSchedd:
   def __init__(self, namespace, trusted_schedds):
      """
      Arguments:
         namespace: string
             Monitored namespace
         trusted_schedds: dictionary, NameRegexp:AuthenticatedIdentityRegexp
             Set of schedds to query. Both name and AuthenticatedIdentity are regexp.
      """
      self.namespace = copy.deepcopy(namespace)
      self.trusted_schedds = copy.deepcopy(trusted_schedds)

   def query_idle(self):
      """Return the list of idle jobs for my namespace"""

      jobs=[]

      sobjs=self._get_schedd_objs()
      for sclassad in sobjs:
         s=htcondor.Schedd(sclassad)
         jobs+=s.xquery(constraint='(JobStatus=?=1)&&(prp_namespace=?="%s")'%self.namespace)

      return jobs


   # INTERNAL
   def _get_schedd_objs(self):
      sobjs=[]
      c = htcondor.Collector()
      slist=c.query(ad_type=htcondor.htcondor.AdTypes.Schedd,projection=['Name','AuthenticatedIdentity','MyAddress','AddressV1','Machine'])
      for s in slist:
         try:
            sname=s['Name']
            sauthid=s['AuthenticatedIdentity']
         except:
            # if I cannot find all, it is invalid
            continue
         if not self._is_valid_schedd(sname,sauthid):
            continue # ignore untrusted schedds
         sobjs.append(s)
         # cleaup to avoid accidental reuse
         del sname
         del sauthid
      return sobjs

   def _is_valid_schedd(self, schedd_name, schedd_authid):
      found = False
      for nameregex in self.trusted_schedds.keys():
         if re.fullmatch(nameregex,schedd_name):
            # found a valid schedd name
            authregex=self.trusted_schedds[nameregex]
            if re.fullmatch(authregex,schedd_authid):
               #it also matches the identity
               found = True
               break # found, we are done
         # ignore all others
      return found

