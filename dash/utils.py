import urllib2
import subprocess
import json

# def untar(file):
#     cmd("tar -xvf %s" % file)
#
# def gunzip(file):
#     cmd("gunzip %s" % file)
#
# def cmd(cmd):
#     subprocess.call(cmd.split(" "))
#
# def import_database(file_path, user, password, database, host="localhost"):
#     with open(file_path, 'r') as f:
#         command = ["mysql", "--user=%s" % user, "--password=%s" % password, "--host=%s" % host, database]
#         proc = subprocess.Popen(command, stdin = f)
#         stdout, stderr = proc.communicate()

def print_json(data):
    print json.dumps(data, indent=4, sort_keys=True)

def format_bytes(value):
    n=value;m=0;f=1e3
    while n>=f:n/=f;m+=2
    return "%.1f%s"%(n,'B kBMBGB'[m:m+2])
