from .api import Api

class Environments(Api):

    def get_environments(self, projet_id, environment_id):
        return self.do_request('/naut/project/{project}/environment/{env}'.format(project=projet_id, env=environment_id))
