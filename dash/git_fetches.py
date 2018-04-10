from .api import Api

class GitFetches(Api):
    def create_git_fetch(self, project_id):
        return self.do_request('/naut/project/%s/git/fetches' % (project_id), None, 'POST')

    def get_git_fetch(self, project_id, id):
        return self.do_request('/naut/project/%s/git/fetches/%s' % (project_id, id))