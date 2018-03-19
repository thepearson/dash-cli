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


class ArgParser(object):

    conofig = None
    def __init__(self, config):
        self.config = config

        parser = argparse.ArgumentParser(
            description='CLI interface with CWP dash',
            usage='''cwp <command> [<sub_cmmand>|<args>]

The most commonly used git commands are:
   stack            Perform actions on stacks
   snapshot         Perform snapshot actions
''')
        parser.add_argument('command', help='Subcommand to run')

        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            print('Unrecognized command')
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

        print("{id}\t\t{created}}\t\t{env}\n---".format(id='ID', created='CREATED', env='ENVIRONMENTS'))

        if single is True:
            stack = stacks['data']
            environments = []
            for environment in stack['relationships']['environments']['data']:
                environments.append(environment['id'])
            print("{id}\t\t{created}\t\t{env}".format(id=stack['id'], created=stack['attributes']['created'], env=", ".join(environments)))
        else:
            for stack in stacks['data']:
                environments = []
                for environment in stack['relationships']['environments']['data']:
                    environments.append(environment['id'])
                print("{id}\t\t{created}\t\t{env}".format(id=stack['id'], created=stack['attributes']['created'], env=", ".join(environments)))


    def snapshot(self):
        parser = argparse.ArgumentParser(
            description='Perform snapshot actions')

        parser.add_argument('sub_command', help='Specify a sub command')
        args = parser.parse_args(sys.argv[2:3])

        if not args.sub_command:
            print('You must specify a sub command')
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


    def transfer_status(self):
        parser = argparse.ArgumentParser(
            description='Check on the transfer status for a snapshot')

        parser.add_argument('project', help='Specify the project')
        parser.add_argument('transfer_id', help='The ID of the transfer to check on, this is output when queuing a new snapshot creation')

        args = parser.parse_args(sys.argv[3:])
        api = get_api('snapshots', self.config)

        snapshot_data = api.get_snapshot_transfer(args.project, args.transfer_id)
        print("Snapshot for '{project}' queued".format(project=args.project))
        print("{id}\t{status}\t\t{project}\n---".format(id='TRANSFER ID', status='STATUS', project='PROJECT'))
        print("{id}\t\t{status}\t\t{project}\n".format(id=snapshot_data['data']['id'], status=snapshot_data['data']['attributes']['status'], project=args.project))


    def download_snapshot(self):
        parser = argparse.ArgumentParser(
            description='Download a snapshot')

        parser.add_argument('project', help='Specify the project')
        parser.add_argument('snapshot_id', help='Specify the snapshot ID to download')

        args = parser.parse_args(sys.argv[3:])
        api = get_api('snapshots', self.config)

        print("Downloading '{project}' snapshot with the following ID: {id}".format(project=args.project, id=args.snapshot_id))
        api.download_snapshot(args.project, args.snapshot_id)
        print("OK.")


    def delete_snapshot(self):
        parser = argparse.ArgumentParser(
            description='Delete a given snapshot id for a project')

        parser.add_argument('project', help='Specify the project')
        parser.add_argument('snapshot_id', help='Specify what snapshot ID to delete')
        args = parser.parse_args(sys.argv[3:])
        api = get_api('snapshots', self.config)

        print("Deleting '{project}' snapshot with the following ID: {id}".format(args.project, args.snapshot_id))
        api.delete_snapshot(args.project, args.snapshot_id)
        print("OK.")


    def create_snapshot(self):
        parser = argparse.ArgumentParser(
            description='Queues a new snapshot creation')

        parser.add_argument('project', help='Specify the project')
        parser.add_argument('snap_type', nargs='?', default='all', help='What type of snapshot to create, db|assets|all')
        parser.add_argument('snap_env', nargs='?', default='uat', help='What environement to use. uat|prod')

        args = parser.parse_args(sys.argv[3:])
        api = get_api('snapshots', self.config)

        snapshot_data = api.create_snapshot(args.project, args.snap_type, args.snap_env)
        print("Snapshot for '{project}' queued".format(project=args.project))
        print("{id}\t{status}\t\t{project}\t\t{type}\t\t{env}\n---".format(id='TRANSFER ID', status='STATUS', project='PROJECT', type='TYPE', env='ENVIRONMENT'))
        print("{id}\t\t{status}\t\t{project}\t\t{type}\t\t{env}\n".format(
            id=snapshot_data['data']['id'],
            status=snapshot_data['data']['attributes']['status'],
            project=args.project,
            type=args.snap_type,
            env=args.snap_env))


    def list_snapshots(self):
        parser = argparse.ArgumentParser(
            description='Lists snapshots for a given project')

        parser.add_argument('project', help='Specify the project')
        args = parser.parse_args(sys.argv[3:])
        api = get_api('snapshots', self.config)

        print("\nRetrieving snapshots for '{project}'\n".format(project=args.project))
        snapshot_data = api.get_snapshots(args.project)
        print("{id}\t\t{type}\t\t{size}\t\t{status}\t\t{env}\t\t{date}\n---".format(id='ID', type='TYPE', size='SIZE', status='STATUS', env='ENV', date='DATE'))

        if 'data' in snapshot_data and len(snapshot_data['data']) > 0:
            for snapshot in snapshot_data['data']:
                print("{id}\t\t{type}\t\t{size}\t\t{status}\t\t{env}\t\t{date}".format(
                    id=snapshot['id'],
                    type=snapshot['attributes']['mode'],
                    size=format_bytes(snapshot['attributes']['size']),
                    status=snapshot['attributes']['snapshot_status'],
                    env=snapshot['relationships']['source']['data'][0]['id'],
                    date=snapshot['attributes']['created']))
