from .api import Api

class GitFetches(Api):

    def create_git_fetch(self, project_id):
        return self.do_request('/naut/project/{project}/git/fetches'.format(project=projet_id), None, 'POST')

    def get_git_fetch(self, project_id, id):
        return self.do_request('/naut/project/{project}/git/fetches/{id}'.format(project=project_id, id=id))
