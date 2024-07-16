#
# prp-htcondor-portal/provisioner
#
# BSD license, copyright Igor Sfiligoi@UCSD 2022
#
# Implement the config parser helper function
#

import copy

def encode_el(v):
  # need a way to propagate : and ,
  while v.find("&colon;")>=0:
    v=v.replace("&colon;",":")
  while v.find("&comma;")>=0:
    v=v.replace("&comma;",",")
  while v.find("&amp;")>=0:
    v=v.replace("&amp;","&")
  return v

def parse_list(list_str):
   out=[]
   for v in list_str.split(','):
     out.append(encode_el(v))
   return out

def parse_dict(dict_str):
   els = dict_str.split(",")
   out = {}
   for el in els:
     k,v = el.split(":")
     out[k] = encode_el(v)
   return out

def update_parse(var, field, ftype,
                 fields, dict):
   """Update var if filed in both fields and dice, and parse according to ftype"""
   if (field in fields) and (field in dict):
      rval=dict[field]
      if (ftype=="str"):
         var = copy.deepcopy(rval)
      elif (ftype=="int"):
         var = int(rval)
      elif (ftype=="list"):
         var = parse_list(rval)
      elif (ftype=="dict"):
         var = parse_dict(rval)
   return var
