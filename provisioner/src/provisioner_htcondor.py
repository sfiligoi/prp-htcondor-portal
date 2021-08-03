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

class ProvisionerSchedd:
   """HTCondor schedd interface"""

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

   def query_idle(self, projection=[]):
      """Return the list of idle jobs for my namespace"""
      return self.query(job_status=1, projection=projection)


   def query(self, job_status, projection=[]):
      """Return the list of jobs for my namespace"""

      jobs=[]

      sobjs=self._get_schedd_objs()
      for sclassad in sobjs:
         s=htcondor.Schedd(sclassad)
         jobs+=s.xquery(constraint='(JobStatus=?=%i)&&(prp_namespace=?="%s")'%(job_status,self.namespace), projection=projection)

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



class ProvisionerClusteredSchedd:
   """HTCondor schedd interface with clustering"""

   def __init__(self, namespace, trusted_schedds):
      """
      Arguments:
         namespace: string
             Monitored namespace
         trusted_schedds: dictionary, NameRegexp:AuthenticatedIdentityRegexp
             Set of schedds to query. Both name and AuthenticatedIdentity are regexp.
      """
      self.schedd=ProvisionerSchedd(namespace, trusted_schedds)

      # fix list of attributes and their defaults here
      self.int_attrs={'RequestCpus':1,
                      'RequestMemory':1024,
                      'RequestDisk':100000,
                      'RequestGPUs':0 }

   def query_idle(self):
      """Return the number of idle jobs by cluster for my namespace"""
      return self.query(job_status=1)


   def query(self, job_status):
      """Return the number of jobs by cluster for my namespace"""

      clusters={}
      jobs=self.schedd.query(job_status=job_status, projection=list(self.int_attrs.keys()))
      for job in jobs:
         cluster_key=[]
         cluster_id={}
         for attr in self.int_attrs:
            try:
               val=job[attr]
               if type(val)==classad.classad.ExprTree:
                  val=val.eval()
               val=int(val)
            except:
               # if anything goes wrong, use default value
               val=self.int_attrs[attr]
            cluster_id[attr]=val
            cluster_key.append(val)

         cluster_key=tuple(cluster_key)
         if cluster_key not in clusters:
            clusters[cluster_key]={'full':cluster_id,'value':0}
         clusters[cluster_key]['value']+=1
      return clusters

