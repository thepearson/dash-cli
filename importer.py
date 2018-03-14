#!/usr/bin/env python
import os
import json
import time
import base64
import urllib2
import argparse
import subprocess
import ConfigParser

def log(message, level = 'info'):
    print message

DEFAULT_CONF='~/.cwpenv'
DEFAULT_ENVIRONMENT='prod'
DEFAULT_TYPE="all"
BASE_URL=''

parser = argparse.ArgumentParser(description='Sync backups from CWP')
parser.add_argument('-c', '--config')
parser.add_argument('-S', '--stack')
parser.add_argument('-e', '--environment')
parser.add_argument('-t', '--type') # ['all', 'db', 'assets']

args = parser.parse_args()

# if args.imp:
#     imp=True
# else:
imp=False

if args.config:
    env=args.config
else:
    env=DEFAULT_CONF

# if not args.stack:
#     log('Please specify a stack')
#     exit(1)
#
# if args.type:
#     log('No type specified, defaulting to `all`')
#     type=args.type
# else:
#     type=DEFAULT_TYPE
#
# if args.environment:
#     log('No environment specified, defaulting to `prod`')
#     environment=args.environment
# else:
#     environment=DEFAULT_ENVIRONMENT
#

environment='prod'
type='db'
stack='moeinside'

config = ConfigParser.ConfigParser()
config.read([env])

api_email = config.get('default', 'api_email')
api_token = config.get('default', 'api_token')

base64string = base64.b64encode('%s:%s' % (api_email, api_token))

headers = {
    'Content-Type': 'application/vnd.api+json',
    'Accept': 'application/vnd.api+json',
    'X-Api-Version': '2.0',
    'Authorization': "Basic %s" % base64string
    }

"""
Stacks
"""
def getStacks():
    req = urllib2.Request('https://dash.cwp.govt.nz/naut/projects', None, headers)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def getStack(id):
    req = urllib2.Request('https://dash.cwp.govt.nz/naut/project/%s' % id,  None, headers)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

"""
Environements
"""
def getEnvironement(project, id):
    req = urllib2.Request('https://dash.cwp.govt.nz/naut/project/%s/environment/%s' % (project, id), None, headers)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

"""
Snapshots
"""
def getSnapshots(project):
    req = urllib2.Request('https://dash.cwp.govt.nz/naut/project/%s/snapshots' % project, None, headers)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def getSnapshot(project, id):
    req = urllib2.Request('https://dash.cwp.govt.nz/naut/project/%s/snapshots/%s' % (project, id), None, headers)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def getSnapshotTransfer(project, id):
    req = urllib2.Request('https://dash.cwp.govt.nz/naut/project/%s/snapshots/transfer/%s' % (project, id), None, headers)
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def deleteSnapshot(project, id):
    req = urllib2.Request('https://dash.cwp.govt.nz/naut/project/%s/snapshots/%s' % (project, id), None, headers)
    req.get_method = lambda: 'DELETE'
    response = urllib2.urlopen(req)
    return response.read()

def deleteAllSnapshots(project):
    snapshots = getSnapshots(project)
    for snapshot in snapshots['data']:
        log("Deleting snapshot %s" % snapshot['id'])
        deleteSnapshot(project, snapshot['id'])

def createSnapshot(project, type, env):
    data = {
        "environment": env,
        "mode": type
    }
    req = urllib2.Request('https://dash.cwp.govt.nz/naut/project/%s/snapshots' % project, json.dumps(data), headers)
    req.get_method = lambda: 'POST'
    response = urllib2.urlopen(req)
    return json.loads(response.read())

def checkTransferComplete(project, transfer_id):
    start_time = time.time()
    complete = False
    while complete == False:
        transfer = getSnapshotTransfer(project, transfer_id)
        if transfer['data']['attributes']['status'] == 'Finished':
            complete = True
        else:
            log("Waiting for %s snapshot to complete... elapsed %d seconds" % (project, time.time() - start_time))
            time.sleep(10)
    return transfer['data']['relationships']['snapshot']

"""
Command line utilities
"""
def downloadFile(src, dest):
    with open(dest, 'wb') as f:
        req = urllib2.Request(src, None, headers)
        f.write(urllib2.urlopen(req).read())
        f.close()
    log("File downloaded as %s." % dest)

def untar(file):
    cmd("tar -xvf %s" % file)

def gunzip(file):
    cmd("gunzip %s" % file)

def cmd(cmd):
    subprocess.call(cmd.split(" "))

def importDb(file_path, user, password, database, host="localhost"):
    with open(file_path, 'r') as f:
        command = ["mysql", "--user=%s" % user, "--password=%s" % password, "--host=%s" % host, database]
        proc = subprocess.Popen(command, stdin = f)
        stdout, stderr = proc.communicate()

def pJson(data):
    print json.dumps(data, indent=4, sort_keys=True)

# log('Deleting previous snapshots')
# deleteAllSnapshots(stack)

# Ask for a snapshot
log('Request new snapshot')
transfer = createSnapshot(stack, type, environment)

# Wait till it's finished
log('Checking status of snapshot')
snapshot_info = checkTransferComplete(stack, transfer['data']['id'])

# Get the file url
log('Getting snapshot details')
snapshot = getSnapshot(stack, snapshot_info['data']['id'])

# Download link
log('Downloading snapshot')
download_link = snapshot['data']['links']['download_link']
downloadFile(download_link, 'download.tar')


if imp == True:
    # untar
    log('Uncompressing database dump')
    untar('download.tar')
    gunzip('database.sql.gz')

    # Import databases file
    log('Importing database')
    importDb('database.sql', config.get('mariadb', 'user'), config.get('mariadb', 'password'), config.get('mariadb', 'schema'))


#deleteAllSnapshots('moeedgazette')
#pJson(getSnapshots('moeedgazette'))
#pJson(checkTransferComplete('moeedgazette', '15272'))
#pJson(getSnapshot('moeedgazette', '13337'))
#pJson(createSnapshot('moeedgazette', 'db', 'prod'))
#pJson(getSnapshots('moeedgazette'))
