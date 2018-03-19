import json

def print_json(data):
    print(json.dumps(data, indent=4, sort_keys=True))

def format_bytes(value):
    n=value;m=0;f=1e3
    while n>=f:n/=f;m+=2
    return "%.1f%s"%(n,'B kBMBGB'[m:m+2])
