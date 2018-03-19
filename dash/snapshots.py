from time import sleep, time
from .api import Api

class Snapshots(Api):

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
            else:
                print "Waiting for %s snapshot to complete... elapsed %d seconds" % (project, time() - start_time)
                sleep(self.delay)
        return transfer['data']['relationships']['snapshot']

    def download_snapshot(self, project, snapshot_id):
        snapshot = self.get_snapshot(project, snapshot_id)
        download_link = snapshot['data']['links']['download_link']
        self.download_request(download_link, "%s-%s-%s-snapshot.sspak" % (project, snapshot['data']['relationships']['source']['data'][0]['id'], snapshot['data']['attributes']['mode']))

    def easy_snapshot(self, project, type, env, filename = 'snapshot.spak'):
        transfer = self.create_snapshot(project, type, env)
        snapshot_info = self.check_transfer_complete(project, transfer['data']['id'])
        snapshot = self.get_snapshot(project, snapshot_info['data']['id'])
        download_link = snapshot['data']['links']['download_link']
        download_file(download_link, filename)
