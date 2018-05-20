from time import sleep, time
from .api import Api

class SnapshotsError(Exception):
    '''raise this when there's an error with a snapshot'''

class Snapshots(Api):

    snapshot_timeout = 10800 # 3 hours

    delay = 10

    def get_snapshots(self, project):
        return self.do_request('/naut/project/%s/snapshots' % project)

    def get_snapshot(self, project, id):
        return self.do_request('/naut/project/%s/snapshots/%s' % (project, id))

    def get_snapshot_transfer(self, project, id):
        return self.do_request('/naut/project/%s/snapshots/transfer/%s' % (project, id))

    def delete_snapshot(self, project, id):
        return self.do_request('/naut/project/%s/snapshots/%s' % (project, id), None, 'DELETE', empty_response=True)

    def delete_all_snapshots(self, project):
        snapshots = self.get_snapshots(project)
        for snapshot in snapshots['data']:
            self.delete_snapshot(project, snapshot['id'])

    def create_snapshot(self, project, type, env):
        data = {
            "environment": env,
            "mode": type
        }
        return self.do_request('/naut/project/%s/snapshots' % project, data, 'POST')

    def check_transfer_complete(self, project, transfer_id):
        start_time = time()
        complete = False
        while complete == False:
            transfer = self.get_snapshot_transfer(project, transfer_id)
            if transfer['data']['attributes']['status'] == 'Finished':
                complete = True
            elif transfer['data']['attributes']['status'] == 'Failed':
                raise SnapshotsError("Snapshot failed")
            else:
                elapsed_time = time() - start_time
                if elapsed_time > self.snapshot_timeout:
                    # Timeout if this takes too long
                    raise SnapshotsError("Snapshot timeout")

                print "Waiting for %s snapshot to complete... elapsed %d seconds" % (project, elapsed_time)
                sleep(self.delay)
        return transfer['data']['relationships']['snapshot']

    def download_snapshot(self, project, snapshot_id):
        snapshot = self.get_snapshot(project, snapshot_id)
        download_link = snapshot['data']['links']['download_link']
        self.download_request(download_link, "%s-%s-%s-snapshot.sspak" % (project, snapshot['data']['relationships']['source']['data'][0]['id'], snapshot['data']['attributes']['mode']))

    def easy_snapshot(self, project, type, env, filename = 'snapshot.spak'):
        print "Create snapshot request"
        transfer = self.create_snapshot(project, type, env)

        try:
            snapshot_info = self.check_transfer_complete(project, transfer['data']['id'])
        except SnapshotsError:
            print "Snapshot failed"
            raise

        print "Downloading snapshot..."
        self.download_snapshot(project, snapshot_info['data']['id'])

        print "Cleaning up API snapshots"
        self.delete_snapshot(project, snapshot_info['data']['id'])
