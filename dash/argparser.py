from .caller import Caller
from .json_serializer import JsonSeriaizer
from .stacks import Stacks
from .environments import Environments
from .git_fetches import GitFetches
from .snapshots import Snapshots

from .utils import format_bytes
import argparse;
import json
import sys

def get_api(type, config):
    caller = Caller(config['base_url'], config['api_email'], config['api_token'])
    serializer = JsonSeriaizer()

    if type == "stacks":
        return Stacks(caller, serializer)

    if type == "environments":
        return Environments(caller, serializer)

    if type == "git_fetches":
        return GitFetches(caller, serializer)

    if type == "snapshots":
        return Snapshots(caller, serializer)

    if type == "deployments":
        return Deployments(caller, serializer)


class ArgParser(object):

    config = None
    def __init__(self, config):
        self.config = config

        parser = argparse.ArgumentParser(
            description='CLI interface with CWP dash',
            usage='''cwp <command> [<sub_cmmand>|<args>]

Top level commands:
   stack            Perform actions on stacks
   snapshot         Perform snapshot actions
   git              Perform git actions
   config           Configure this
''')
        parser.add_argument('command', help='Subcommand to run')

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print 'Unrecognized command'
            parser.print_help()
            exit(1)

        # use dispatch pattern to invoke method with same name
        getattr(self, args.command)()


    def stack(self):
        parser = argparse.ArgumentParser(
            description='List available stacks or specific stack')

        single = False
        parser.add_argument('-p', '--project', help='Limits the response to specific projects')
        args = parser.parse_args(sys.argv[2:4])

        api = get_api('stacks', self.config)
        if args.project:
            stacks = api.get_stack(args.project)
            single = True
        else:
            stacks = api.get_stacks()

        print "%s\t\t%s\t\t%s\n---" % ('ID', 'CREATED', 'ENVIRONMENTS')
        if single is True:
            stack = stacks['data']
            environments = []
            for environment in stack['relationships']['environments']['data']:
                environments.append(environment['id'])
            print "%s\t\t%s\t\t%s" % (stack['id'], stack['attributes']['created'], ", ".join(environments))
        else:
            for stack in stacks['data']:
                environments = []
                for environment in stack['relationships']['environments']['data']:
                    environments.append(environment['id'])
                print "%s\t\t%s\t\t%s" % (stack['id'], stack['attributes']['created'], ", ".join(environments))


    def snapshot(self):
        parser = argparse.ArgumentParser(
            description='Perform snapshot actions')

        parser.add_argument('sub_command', help='Specify a sub command')
        args = parser.parse_args(sys.argv[2:3])

        if not args.sub_command:
            print 'You must specify a sub command'
            parser.print_help()
            exit(1)

        if args.sub_command == 'list':
            getattr(self, 'list_snapshots')()

        if args.sub_command == 'create':
            getattr(self, 'create_snapshot')()

        if args.sub_command == 'status':
            getattr(self, 'transfer_status')()

        if args.sub_command == 'delete':
            getattr(self, 'delete_snapshot')()

        if args.sub_command == 'download':
            getattr(self, 'download_snapshot')()

        if args.sub_command == 'simple':
            getattr(self, 'simple_snapshot')()


    def git(self):
        parser = argparse.ArgumentParser(
            description='Perform snapshot actions')

        parser.add_argument('sub_command', help='Specify a sub command')
        args = parser.parse_args(sys.argv[2:3])

        if args.sub_command == 'fetch':
            getattr(self, 'git_fetch')()

        if args.sub_command == 'status':
            getattr(self, 'git_status')()


    def git_status(self):
        parser = argparse.ArgumentParser(
            description='Check on the status for a git fetch')

        parser.add_argument('project', help='Specify the project')
        parser.add_argument('fetch_id', help='The ID of the git fetch to check on, this is output when queuing a new git fetch')

        args = parser.parse_args(sys.argv[3:])

        api = get_api('git_fetches', self.config)
        if not args.project:
            print "Please specify project"
            exit(1)

        fetches_data = api.get_git_fetch(args.project, args.fetch_id)
        print "Git fetch for '%s' queued" % args.project
        print "%s\t%s\t\t%s\n---" % ('FETCH ID', 'STATUS', 'PROJECT')
        print "%s\t\t%s\t\t%s\n" % (fetches_data['data']['id'], fetches_data['data']['attributes']['status'], args.project)


    def git_fetch(self):
        parser = argparse.ArgumentParser(
            description='Create a git fetch on the repo for this project')

        parser.add_argument('project', help='Specify the project')

        args = parser.parse_args(sys.argv[3:])

        api = get_api('git_fetches', self.config)
        if not args.project:
            print "Please specify project"
            exit(1)

        fetches_data = api.create_git_fetch(args.project)
        print "Git fetch for '%s' queued" % args.project
        print "%s\t%s\t\t%s\n---" % ('FETCH ID', 'STATUS', 'PROJECT')
        print "%s\t\t%s\t\t%s\n" % (fetches_data['data']['id'], fetches_data['data']['attributes']['status'], args.project)



    def transfer_status(self):
        parser = argparse.ArgumentParser(
            description='Check on the transfer status for a snapshot')

        parser.add_argument('project', help='Specify the project')
        parser.add_argument('transfer_id', help='The ID of the transfer to check on, this is output when queuing a new snapshot creation')

        args = parser.parse_args(sys.argv[3:])

        api = get_api('snapshots', self.config)
        if not args.project:
            print "Please specify project"
            exit(1)

        snapshot_data = api.get_snapshot_transfer(args.project, args.transfer_id)
        print "Snapshot for '%s' queued" % args.project
        print "%s\t%s\t\t%s\n---" % ('TRANSFER ID', 'STATUS', 'PROJECT')
        print "%s\t\t%s\t\t%s\n" % (snapshot_data['data']['id'], snapshot_data['data']['attributes']['status'], args.project)


    def simple_snapshot(self):
        parser = argparse.ArgumentParser(
            description='Queues a new snapshot creation')

        parser.add_argument('project', help='Specify the project')
        parser.add_argument('snap_type', nargs='?', default='all', help='What type of snapshot to create, db|assets|all')
        parser.add_argument('snap_env', nargs='?', default='uat', help='What environement to use. uat|prod')

        args = parser.parse_args(sys.argv[3:])

        api = get_api('snapshots', self.config)
        if not args.project:
            print "Please specify project"
            exit(1)

        snapshot_data = api.easy_snapshot(args.project, args.snap_type, args.snap_env)
        print "OK."


    def download_snapshot(self):
        parser = argparse.ArgumentParser(
            description='Download a snapshot')

        parser.add_argument('project', help='Specify the project')
        parser.add_argument('snapshot_id', help='Specify the snapshot ID to download')

        args = parser.parse_args(sys.argv[3:])

        api = get_api('snapshots', self.config)
        if not args.project:
            print "Please specify project"
            exit(1)

        print "Downloading '%s' snapshot with the following ID: %s" % (args.project, args.snapshot_id)
        api.download_snapshot(args.project, args.snapshot_id)
        print "OK."


    def delete_snapshot(self):
        parser = argparse.ArgumentParser(
            description='Delete a given snapshot id for a project')

        parser.add_argument('project', help='Specify the project')
        parser.add_argument('snapshot_id', help='Specify what snapshot ID to delete')

        args = parser.parse_args(sys.argv[3:])

        api = get_api('snapshots', self.config)
        if not args.project:
            print "Please specify project"
            exit(1)

        print "Deleting '%s' snapshot with the following ID: %s" % (args.project, args.snapshot_id)
        api.delete_snapshot(args.project, args.snapshot_id)
        print "OK."


    def create_snapshot(self):
        parser = argparse.ArgumentParser(
            description='Queues a new snapshot creation')

        parser.add_argument('project', help='Specify the project')
        parser.add_argument('snap_type', nargs='?', default='all', help='What type of snapshot to create, db|assets|all')
        parser.add_argument('snap_env', nargs='?', default='uat', help='What environement to use. uat|prod')

        args = parser.parse_args(sys.argv[3:])

        api = get_api('snapshots', self.config)
        if not args.project:
            print "Please specify project"
            exit(1)

        snapshot_data = api.create_snapshot(args.project, args.snap_type, args.snap_env)
        print "Snapshot for '%s' queued" % args.project
        print "%s\t%s\t\t%s\t\t%s\t\t%s\n---" % ('TRANSFER ID', 'STATUS', 'PROJECT', 'TYPE', 'ENVIRONMENT')
        print "%s\t\t%s\t\t%s\t\t%s\t\t%s\n" % (snapshot_data['data']['id'], snapshot_data['data']['attributes']['status'], args.project, args.snap_type, args.snap_env)


    def list_snapshots(self):
        parser = argparse.ArgumentParser(
            description='Lists snapshots for a given project')

        parser.add_argument('project', help='Specify the project')

        args = parser.parse_args(sys.argv[3:])

        api = get_api('snapshots', self.config)
        if not args.project:
            print "Please specify project"
            exit(1)

        print "\nRetrieving snapshots for '%s'\n" % args.project
        snapshot_data = api.get_snapshots(args.project)
        print "%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%s\n---" % ('ID', 'TYPE', 'SIZE', 'STATUS', 'ENV', 'DATE')

        if 'data' in snapshot_data and len(snapshot_data['data']) > 0:
            for snapshot in snapshot_data['data']:
                print "%s\t\t%s\t\t%s\t\t%s\t%s\t\t%s" % (snapshot['id'],
                    snapshot['attributes']['mode'],
                    format_bytes(snapshot['attributes']['size']),
                    snapshot['attributes']['snapshot_status'],
                    snapshot['relationships']['source']['data'][0]['id'],
                    snapshot['attributes']['created'])

    def config(self):
        parser = argparse.ArgumentParser(
            description='Download objects and refs from another repository')
        parser.add_argument('repository')
        args = parser.parse_args(sys.argv[2:])
        print 'Running cwp config, repository=%s' % args.repository
