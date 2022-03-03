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
import classad

ProvisionerHTCConfigFields = ('namespace','condor_host',
                              'app_name','k8s_domain')

class ProvisionerHTCConfig:
   """Config file for HTCOndor provisioning classes"""

   def __init__(self, namespace,
                condor_host="prp-cm-htcondor.htcondor-portal.svc.cluster.local",
                app_name = 'prp-wn',
                k8s_domain='optiputer.net'):
      self.namespace = copy.deepcopy(namespace)
      self.condor_host = copy.deepcopy(condor_host)
      self.app_name = copy.deepcopy(app_name)
      self.k8s_domain = copy.deepcopy(k8s_domain)

   def parse(self,
             dict,
             fields=ProvisionerHTCConfigFields):
      """Parse the valuies from a dictionary"""
      self.namespace = update_parse(self.namespace, 'namespace', 'str', fields, dict)
      self.condor_host = update_parse(self.condor_host, 'condor_host', 'str', fields, dict)
      self.k8s_domain = update_parse(self.k8s_domain, 'k8s_domain', 'str', fields, dict)
      self.app_name = update_parse(self.app_name, 'app_name', 'str', fields, dict)

class ProvisionerSchedd:
   """HTCondor schedd interface"""

   def __init__(self, trusted_schedds, config):
      """
      Arguments:
         namespace: string
             Monitored namespace
         trusted_schedds: dictionary, NameRegexp:AuthenticatedIdentityRegexp
             Set of schedds to query. Both name and AuthenticatedIdentity are regexp.
      """
      self.namespace = copy.deepcopy(config.namespace)
      self.trusted_schedds = copy.deepcopy(trusted_schedds)

   def query_idle(self, projection=[]):
      """Return the list of idle jobs for my namespace"""
      return self.query(job_status=1, projection=projection)


   def query(self, job_status, projection=[]):
      """Return the list of jobs for my namespace"""

      full_projection=['ClusterId','ProcId','JobStatus','RequestK8SNamespace']+projection
      jobs=[]

      sobjs=self._get_schedd_objs()
      for sclassad in sobjs:
         s=htcondor.Schedd(sclassad)
         myjobs=s.xquery('(JobStatus=?=%i)&&regexp(RequestK8SNamespace,"%s")'%(job_status,self.namespace), full_projection)
         self._append_jobs(sclassad['Name'], jobs, myjobs)

      return jobs


   # INTERNAL
   def _append_jobs(self, schedd_name, jobs, myjobs):
      """jobs is a list and will be updated in-place"""
      minvals={'RequestMemory':4096,'RequestDisk':8000000}
      for job in myjobs:
         jobattrs={'ScheddName':schedd_name}
         for k in job.keys():
            if k in minvals.keys():
               # the default RequestMemory and RequestDisk in condor is dynamic
               # and the initial value (after eval) is way too low
               # Treat very low values as undefines
               val = int(job.eval(k))
               if val>=minvals[k]:
                  jobattrs[k]="%s"%val
               #else pretend it is not there
            else:
               # convert all values to strings, for easier management
               # also expand all expresstions
               jobattrs[k]="%s"%job.eval(k)
         jobs.append(jobattrs)
      return

   def _get_schedd_objs(self):
      sobjs=[]
      c = htcondor.Collector()
      slist=c.query(ad_type=htcondor.AdTypes.Schedd,projection=['Name','AuthenticatedIdentity','MyAddress','AddressV1','Machine'])
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


class ProvisionerCollector:
   """HTCondor Collector/startd interface"""

   def __init__(self, startd_identity, config):
      """
      Arguments:
         namespace: string
             Monitored namespace
         startd_identity: string
             AuthenticatedIdentity Regexp used as a whitelist
      """
      self.namespace = copy.deepcopy(config.namespace)
      self.k8s_domain = copy.deepcopy(config.k8s_domain)
      self.startd_identity = copy.deepcopy(startd_identity)

   def query(self,  projection=[]):
      """Return the list of startds for my namespace"""

      full_projection=['Name','AuthenticatedIdentity','State','Activity','K8SPodName','K8SNamespace', 'K8SDomain']+projection
      startds=[]

      c = htcondor.Collector()
      slist=c.query(ad_type=htcondor.AdTypes.Startd,projection=full_projection,
                    constraint='(K8SNamespace=?="%s")&&(K8SDomain=?="%s")'%(self.namespace,self.k8s_domain))
      for s in slist:
         try:
            sname=s['Name']
            sauthid=s['AuthenticatedIdentity']
         except:
            # if I cannot find all, it is invalid
            continue
         if not re.fullmatch(self.startd_identity,sauthid):
            # not trusted, ignore
            continue
         adattrs={}
         for k in s.keys():
            # convert all values to strings, for easier management
            # also eval any expressions
            adattrs[k]="%s"%s.eval(k)
         startds.append(adattrs)
         # cleaup to avoid accidental reuse
         del sname
         del sauthid

      return startds

