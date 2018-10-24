# CWP Dash CLI

This is a command line interface tool for interacting with the NZ Common Web Platform Dash API. The primary aim of this tool is to be supported easily on linux hosts without additional packages having being installed. While it could be implemented easily in many different frameworks/languages, it's written in Python for the simple reason that **most** linux servers support Python out of the box. This package uses no external libraries and only core Python modules.

## Support

Currently dash-cli supports <= Python 2.7. A version supporting Python >= 3 is actively being worked on.

## Installation

You'll need to navigate to https://dash.cwp.govt.nz/naut/profile and obtain an `API token` before continuing.

```
$ sudo pip install dash-cli
$ dash-cli

Executing dash version 0.1.0.
Config file not found, lets get configured

CWP Email Address: [CWP_DASH_EMAIL]
CWP API Token:  [CWP_DASH_API_TOKEN]
You are now configured
```

## Roadmap

* Locks
* Git Fetches
* Deployments
* `sspak` integration

## Usage

```
$ dash-cli -h

Executing dash version 0.1.0.
usage: cwp <command> [<sub_cmmand>|<args>]

Top level commands:
   stack            Perform actions on stacks
   snapshot         Perform snapshot actions

CLI interface with CWP dash

positional arguments:
  command     Subcommand to run

optional arguments:
  -h, --help  show this help message and exit
```

### Listing stacks
```
# List all stacks/projects
$ dash-cli stacks

# List info about a single stack/project
$ dash-cli stack --project=[project_id]
```

### Snapshots

#### List snapshots

Lists all snapshots for a given stack.

```
$ dash-cli snapshot list [project_id]
Executing dash version 0.1.0.

Retrieving snapshots for '[project_id]'

ID      TYPE    SIZE      STATUS    ENV   DATE
---
12345   all     2.3GB     complete  uat   2018-03-19 11:44:05
67890   db      90.0MB    complete  prod  2018-03-13 15:25:05
```

#### Create snapshot

Queues a snapshot creation for a given stack. The request creates a **transfer** which is essentially a queued job, the transfer ID returned can be used with `snapshot status` to query the state of the snapshot transfer.

```
$ dash-cli snapshot create [project_id] [snap_type] [snap_env]
Executing dash version 0.1.0.
Snapshot for 'moeedgazette' queued
TRANSFER ID	STATUS		PROJECT		TYPE		ENVIRONMENT
---
12345		n/a		[project_id]		db		prod

```


#### Query snapshot transfer status

```
$ dash-cli snapshot status [project_id] [transfer_id]
Executing dash version 0.1.0.
Snapshot for '[project_id]' queued
TRANSFER ID	  STATUS		PROJECT
---
12345         Started		[project_id]

```


#### Delete snapshot

```
$ dash-cli snapshot delete [project_id] [snapshot_id]
Executing dash version 0.1.0.
Deleting '[project_id]' snapshot with the following ID: 12345
OK.
```

#### Download snapshot

```
$ dash-cli snapshot download [project_id] [snapshot_id]
Executing dash version 0.1.0.
Downloading 'moeinside' snapshot with the following ID: 12345
OK.

```
