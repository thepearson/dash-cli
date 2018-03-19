from .api import Api

class Stacks(Api):

    def get_stacks(self):
        return self.do_request('/naut/projects')

    def get_stack(self, id):
        return self.do_request('/naut/project/%s' % id)
