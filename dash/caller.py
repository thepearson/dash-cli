import urllib2
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
        return b64encode('%s:%s' % (self.api_email, self.api_token))


    def get_request_headers(self):
        return {
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json',
            'X-Api-Version': '2.0',
            'Authorization': "Basic %s" % self.get_auth_header()
        }


    def do_request(self, request_url, data = None, method = None):
        req = urllib2.Request('%s%s' % (self.base_url, request_url), data, self.get_request_headers())
        if method:
            req.get_method = lambda: method
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError:
            print "Error opening ury %s" % request_url

        return response.read()

    def download_stream(self, src, dest):
        req = urllib2.Request(src, None, self.get_request_headers())
        response = urllib2.urlopen(req)
        CHUNK = 16 * 1024
        with open(dest, 'wb') as f:
            while True:
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                f.write(chunk)


    def download_request(self, src, dest):
        with open(dest, 'wb') as f:
            req = urllib2.Request(src, None, self.get_request_headers())
            f.write(urllib2.urlopen(req).read())
            f.close()
