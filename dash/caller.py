import urllib.request as urllib2
from base64 import b64encode

class Caller():

    api_version = ''
    base_url = ''
    api_token = ''
    api_email = ''


    def __init__(self, base_url='', api_email='', api_token = '', api_version = '2,0'):
        self.api_version = api_version
        self.base_url = base_url
        self.api_email = api_email
        self.api_token = api_token


    def get_auth_header(self):
        string = '{user}:{password}'.format(user=self.api_email, password=self.api_token)
        return b64encode(string.encode('ascii'))


    def get_request_headers(self):
        return {
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json',
            'X-Api-Version': '2.0',
            'Authorization': "Basic {auth}".format(auth=self.get_auth_header())
        }


    def do_request(self, request_url, data = None, method = None):
        req = urllib2.Request('{base}{url}'.format(base=self.base_url, url=request_url), data, self.get_request_headers())
        if method:
            req.get_method = lambda: method
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            print(e)
            print("Error opening url {url}".format(url=request_url))

        return response.read()


    def download_request(self, src, dest):
        with open(dest, 'wb') as f:
            req = urllib2.Request(src, None, self.get_request_headers())
            f.write(urllib2.urlopen(req).read())
            f.close()
