
#!/usr/bin/python

## ********************************************************************************
## get-yarn-usage.py 
## 
## Usage: ./get-hive-usage-user.py
## 
## Edit the settings below to connect to your Cluster
## 
## ********************************************************************************

import sys
from datetime import datetime, timedelta
import pprint
from cm_api.api_client import ApiResource

## Settings to connect to the cluster 

cm_host = "mdonsky-1.gce.cloudera.com"

cm_port = "7180"

cm_login = "admin"

cm_password = "admin"

cluster_name = "Cluster 1" 



## Get command line args

user_name = None
if len(sys.argv) == 2:
  user_name = sys.argv[1]
else:
  print " Usage:  ./get-hive-usage-user.py <user_name>"
  quit(1)


## Used for formatting dates
fmt = '%Y-%m-%d %H:%M:%S %Z'

#  pretty printer for printing JSON attribute lists
pp = pprint.PrettyPrinter(indent=4)

## Connect to CM
print "\nConnecting to Cloudera Manager at " + cm_host + ":" + cm_port
api = ApiResource(server_host=cm_host, server_port=cm_port, username=cm_login, password=cm_password)

## Get Cluster
cluster = None
clusters = api.get_all_clusters()
for c in clusters:
  if c.displayName == cluster_name:
    cluster = c
    break
if cluster is None:
  print "\nError: Cluster '" + cluster_name + "' not found"
  quit(1)


## Get YARN Service
yarn_service = None
service_list = cluster.get_all_services()
for service in service_list:
  if service.type == "YARN":
    yarn_service = service
    break
if yarn_service is None:
  print "Error: Could not locate YARN Service"
  quit(1)

now = datetime.utcnow()
start = now - timedelta(days=60)

filterStr = 'user = '+user_name

yarn_apps_response = yarn_service.get_yarn_applications(start_time=start, end_time=now, filter_str=filterStr, limit=1000)
yarn_apps = yarn_apps_response.applications

## Iterate over the jobs
for i in range (0, len(yarn_apps)):
  yarn_app = yarn_apps[i]
  
  ## Get the Hive SQL
  hive_query_string = yarn_app.attributes.get("hive_query_string",None)
  if hive_query_string is not None:
    print "\n-- YARN Job ID: " + yarn_app.applicationId + " --------------"
    print "YARN App Name: " + yarn_app.name
    print "YARN User: " + yarn_app.user
    print "State: " + yarn_app.state
    print "Hive Query: " + hive_query_string

