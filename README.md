# nagrestconf-python
python API binding for mclarkson/nagrestconf

Aim: Can be used as a standalone tool to run REST commands or included in Python code and use a APi binding

CLI usage:
\# nagrestconf.py -s <server> -r <request> [ -d <data> | -p | -v ]
  -s        Server URI to connect to. It may include HTTP auth data. Ex: https://user:password@restserver/rest
  -r        Request to run: show/hosts, apply/nagiosconfig, etc.
  -d        Data passed for the request, set of data pairs separated by comma
  -p        Run POST request (Needed for all calls except for check and show)
  -v        Verbose level. Default verbosity is ERROR. Each -v increases the log level by one step

# nagrestconf.py -s https://user:pass@nagrestconf.my.org/rest -r show/hosts
# nagrestconf.py -s https://user:pass@nagrestconf.my.org/rest -r modify/hosts -d name:host1,ipaddress:10.10.10.10 -p


Python usage example:

#python
from nagrestconf import nagrestconf
import logging

def objSeek(obj,name):
  for ind,val in enumerate(obj):
    if name in val:
        return val[name]
  return None

nrc=nagrestconf('https://user:pass@nagrestconf.my.org/rest')

# list all hosts
res,naghosts=nrc.showhosts()
if not res:
  logging.exception('Failed to get list of hosts from nagrestconf with error: %s',naghosts)
  
# look for teh host in the nagrestconf dump
for naghid,nagh in enumerate(naghosts):
  # in case the host exists in nagrestconf
  print objSeek(nagh, 'name'), objSeek(nagh, 'ipaddress')

      
      


