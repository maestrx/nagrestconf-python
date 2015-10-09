#!/usr/bin/python  -W ignore
#===============================================================================
#
#          FILE: nagrestconf.py
#   DESCRIPTION: Python binginf for NagRestConf REST interface
#  REQUIREMENTS: pycurl, json, urllib, StringIO, ConfigParser
#        RETURN: 0 - OK
#          BUGS: ---
#         NOTES: Validated using python 2.6
#        AUTHOR: vit.safar@gemalto.com
#  ORGANIZATION:
#       CREATED: 9/10/15
#      REVISION: 1.1
#===============================================================================


import sys
import os
import logging
import pycurl
import json
from urllib import urlencode
from StringIO import StringIO

class nagrestconf:

  _folder=None
  _server_uri=None
  
  _http_contimeout=5
  _http_timeout=30
  
  def __init__(self,server_uri=None,folder=None,log=40):

    try:
      self._folder=folder        
      self._server_uri=server_uri        

      var_mask = ['http_proxy','https_proxy','no_proxy']
      for key in os.environ.keys():
        if key.lower() in var_mask:
          del os.environ[key]

      logging.basicConfig(level=log, format='%(asctime)s [%(levelname)s] %(message)s')

    except Exception, e:
      logging.exception('Unable to init the nagrestconf!')
      return false

  def _run(self,req=False,param={},post=False):
    logging.info('run: Request %s',(req))

    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.FOLLOWLOCATION, True) # Follow redirect.
    c.setopt(c.WRITEFUNCTION, buffer.write)
    c.setopt(c.CONNECTTIMEOUT,self._http_contimeout)
    c.setopt(c.TIMEOUT,self._http_timeout)
    c.setopt(c.SSL_VERIFYPEER,False)

    param.update({'folder':'local'})
    param=urlencode({'json':json.dumps(param)})
    if post:
      c.setopt(c.URL, '{0}/{1}'.format(self._server_uri,req) )
      c.setopt(c.POSTFIELDS, param)
      logging.debug('run.POST: %s/%s with data: "%s"',self._server_uri,req,json.dumps(param))
    else:
      c.setopt(c.URL, '{0}/{1}?{2}'.format(self._server_uri,req,param))
      logging.debug('run.GET: %s/%s?%s',self._server_uri,req,param)

    c.perform()
    logging.info('run.HTTP response code: %s',c.getinfo(c.RESPONSE_CODE))
    body = buffer.getvalue()
    if c.getinfo(c.RESPONSE_CODE)!=200:
      logging.error('run.Server responded with HTTP result code %s and body %s',c.getinfo(c.RESPONSE_CODE),body)
      return [False,'HTTP response code: {0}'.format(c.getinfo(c.RESPONSE_CODE))]
    c.close()
    buffer.close()
    logging.debug('run.HTTP response body: %s',body)

    # parse request results
    try:
      resjson = json.loads(body)
    except:
      logging.error('Unable to parse server response: %s',body)
      return [False,'Unable to parse server response: {0}'.format(body)]
    logging.debug('run.Decoded response JSON: %s',resjson)

    try:
        if isinstance(resjson, (list, tuple)) and len(resjson)==0 :
            return [True,[]]
        elif isinstance(resjson[0], (list, tuple)):
            return [True,resjson]
        elif isinstance(resjson[0], basestring) and resjson[0][:13]=='NAGCTL ERROR:':
            return [False,resjson]
        else:
            return [True,resjson]
    except:
        logging.error('Unable to interpret server response: %s',resjson)
        return [False,'Unable to interpret server response: {0}'.format(resjson)]

  # set log options
  def setLog(self,loglevel=40):
    logging.getLogger().setLevel(loglevel)

  # check
  def checkconfig(self):
    return self._run('check/nagiosconfig')

  # show
  def showhosts(self,name=None):
    filter={}
    if name:
        filter.update({'filter':name})
    return self._run('show/hosts',filter)

  def showservices(self,name=None):
    filter={}
    if name:
        filter.update({'filter':name})
    return self._run('show/services',filter)

  def showcontacts(self,name=None):
    filter={}
    if name:
        filter.update({'filter':name})
    return self._run('show/contacts',filter)

  def showcommands(self,name=None):
    filter={}
    if name:
        filter.update({'filter':name})
    return self._run('show/commands',filter)

  # add
  def addhosts(self,data={}):
    if len(data['name'])<1 and len(data['alias'])<1 and len(data['ipaddress'])<1 and len(data['template'])<1 and len(data['hostgroup'])<1:
        return [False,'Following inputs is mandatory: name, alias, ipaddress, template, hostgroup']
    return self._run('add/hosts',data,True)

  def addservices(self,data={}):
    if len(data['name'])<1 and len(data['contacts'])<1 and len(data['template'])<1 and len(data['command'])<1 and len(data['svcdesc'])<1:
        return [False,'Following inputs is mandatory: name, contacts, template, command, svcdesc']
    return self._run('add/services',data,True)

  def addcontacts(self,data={}):
    if len(data['name'])<1 and len(data['alias'])<1 and len(data['emailaddr'])<1 and len(data['svcnotifperiod'])<1 and len(data['svcnotifopts'])<1 and len(data['svcnotifcmds'])<1 and len(data['hstnotifperiod'])<1 and len(data['hstnotifopts'])<1 and len(data['hstnotifcmds'])<1:
        return [False,'Following inputs is mandatory: name, alias, emailaddr, svcnotifperiod, svcnotifopts, svcnotifcmds, hstnotifperiod, hstnotifopts, hstnotifcmds']
    return self._run('add/contacts',data,True)

  def addcommands(self,data={}):
    # name, command
    return self._run('add/commands',data,True)

  # delete
  def deletehosts(self,data={}):
    return self._run('delete/hosts',data,True)

  def deleteservices(self,data={}):
    return self._run('delete/services',data,True)

  def deletecontacts(self,data={}):
    return self._run('delete/contacts',data,True)

  def deletecommands(self,data={}):
    return self._run('delete/commands',data,True)

  # modify
  def modifyhosts(self,data={}):
    return self._run('modify/hosts',data,True)

  def modifyservices(self,data={}):
    return self._run('modify/services',data,True)

  def modifycontacts(self,data={}):
    return self._run('modify/contacts',data,True)

  def modifycommands(self,data={}):
    return self._run('modify/commands',data,True)

  # restart
  def restart(self):
    return self._run('restart/nagios',{},True)

  # apply
  def applyconfig(self):
    return self._run('apply/nagiosconfig',{},True)

  def applylastconfig(self):
    return self._run('apply/nagioslastgoodconfig',{},True)



if __name__ == "__main__":
  import argparse
  import ConfigParser

  def objSeek(obj,name):
    for ind,val in enumerate(obj):
      if name in val:
          return val[name]
    return None

  reqshort={
'cn':['check/nagiosconfig',False],
'sh':['show/hosts',False], 'ss':['show/services',False], 'sn':['show/contacts',False], 'sm':['show/commands',False] ,
'mh':['modify/hosts',True], 'ms':['modify/services',True], 'mn':['modify/contacts',True], 'mm':['modify/commands',True] ,
'dh':['delete/hosts',True], 'ds':['delete/services',True], 'dn':['delete/contacts',True], 'dm':['delete/commands',True] ,
'ah':['add/hosts',True], 'as':['add/services',True], 'an':['add/contacts',True], 'am':['add/commands',True] ,
'rn':['restart/nagios',True],
'nc':['apply/nagiosconfig',True], 'nll':['apply/nagioslastgoodconfig',True] }

  data={}
  filter={}
  post=False
  log=40
  jout=False
  sep="\t"
  conffile=os.path.expanduser("~/.nagrestconf")

  try:
    parser = argparse.ArgumentParser(description='NagRESTConf API')
    parser.add_argument('-s','--server', help='Server URI to connect to. It may include HTTP auth data. Ex: https://user:password@restserver/rest')
    parser.add_argument('-r','--request', help="Request to run: show/hosts, apply/nagiosconfig, etc. OR shortcuts: \
cn => check/nagiosconfig , \
sh => show/hosts , ss => show/services , sn => show/contacts , sm => show/commands , \
mh => modify/hosts , ms => modify/services , mn => modify/contacts , mm => modify/commands , \
dh => delete/hosts , ds => delete/services , dn => delete/contacts , dm => delete/commands , \
ah => add/hosts , as => add/services , an => add/contacts , am => add/commands , \
rn => restart/nagios , \
nc => apply/nagiosconfig , nl => apply/nagioslastgoodconfig")
    parser.add_argument('-p','--post', action='store_true', help='Run POST request. Needed for all calls except for check and show.')
    parser.add_argument('-j','--json', action='store_true', help='Show result in JSON format')
    parser.add_argument('-d','--data', help='Request data pairs (name:value) separated by comma with no spaces. Ex: name:monitoredhost1,svcdesc:ssh,command:check_ssh')
    parser.add_argument('-v', '--verbose', action='count', help='Verbose level. Default verbosity is ERROR. Each -v increases the log level by one step')
    parser.add_argument('-D','--delimiter', help='Delimiter for the pipe output')
    parser.add_argument('-f','--filter', help='Filter rule pairs (name:value) separated by comma with no spaces. Ex: name:monitoredhost1,svcdesc:ssh,command:check_ssh')

    args = vars(parser.parse_args())
    if args['server']!=None:
      server=args['server']
    else:
      if os.path.isfile(conffile):
        try:
          conf = ConfigParser.RawConfigParser()
          conf.read(conffile)
          server = conf.get('client', 'server')
        except:
          print 'Failed to read server from config file {0}!'.format(conffile)
          sys.exit(1)
      else:
          print 'Server have to be specified!'
          sys.exit(1)

    if args['post']!=False:
      post=True

    if args['json']!=False:
      jout=True

    if args['delimiter']!=None:
        sep=args['delimiter']

    if args['request']!=None:
        if args['request'] in reqshort:
            req=reqshort[args['request']][0]
            post=reqshort[args['request']][1]
        else:
            req=args['request']
    else:
      print 'request have to be specified!'
      sys.exit(1)


    if args['verbose']>0:
      log=40-args['verbose']*10
    logging.getLogger().setLevel(log)

    if args['data']!=None:
      params=args['data'].split(',')
      for param in params:
        try:
            param=param.split(':')
            data.update({param[0]:param[1]})
        except:
            logging.exception('Data argument has to have syntax: <name>:<value>[,<name2>:<value2>,...]  ')
            sys.exit(2)

    if args['filter']!=None:
      filters=args['filter'].split(',')
      for filt in filters:
        try:
            filt=filt.split(':')
            filter.update({filt[0]:filt[1]})
        except:
            logging.exception('Filter argument has to have syntax: <name>:<value>[,<name2>:<value2>,...]  ')
            sys.exit(2)

    nrc=nagrestconf(server,'folder',log)
    ret=nrc._run(req,data,post)
    if ret[0]:
        if isinstance(ret[1][0], (list, tuple)):
            if len(filter)>0:
                prefilter=ret[1]
                ret[1]=[]
                for dat in prefilter:
                    match=True
                    for filt in filter.items():
                        f=objSeek(dat,filt[0])
                        if not (f==None or f==filt[1]):
                            match=False
                    if match:
                        ret[1].append(dat)

            if sys.stdout.isatty():
                if jout:
                    print json.dumps(ret[1])
                else:
                    print 'Result array:'
                    for elem in ret[1]:
                        print "Element:"
                        for atr in elem:
                            (aind,aval)=atr.items()[0]
                            if len(aval)>0:
                                print '{0}{1:22}{2}'.format(' '*10,aind+':',aval)
                        print
            else:
                if jout:
                    print json.dumps(ret[1])
                else:
                    first=True
                    for elem in ret[1]:
                        # show output header
                        if first:
                            for atr in elem:
                                sys.stdout.write('{0}{1}'.format(atr.items()[0][0],sep))
                            print
                            first=False
                        for atr in elem:
                            sys.stdout.write('{0}{1}'.format(atr.items()[0][1],sep))
                        print



        elif isinstance(ret[1][0], basestring):
            if sys.stdout.isatty():
                if jout:
                    print json.dumps(ret[1])
                else:
                    print 'Result string:'
                    for elem in ret[1]:
                       print elem
            else:
                if jout:
                    print json.dumps(ret[1])
                else:
                    print "Result_string",
                    for elem in ret[1]:
                       print "\n{0}".format(elem)
        else:
            if sys.stdout.isatty():
                if jout:
                    print json.dumps(ret[1])
                else:
                    print 'Result: {0}'.format(ret[1])
            else:
                if jout:
                    print json.dumps(ret[1])
                else:
                    print "Result\n{0}".format(ret[1])
    else:
        print 'Failed with reason: {0}'.format(ret[1])

  except SystemExit:
    pass
  except:
    logging.exception('Unable to process the request! Exiting.')
    sys.exit(2)




