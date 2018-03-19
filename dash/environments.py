from .api import Api

class Environments(Api):

    def get_environments(self, projet_id, environment_id):
        return self.do_request('/naut/project/%s/environment/%s' % (projet_id, environment_id))
