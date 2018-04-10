class Api():

    caller = None
    serializer = None


    def __init__(self, caller, serializer):
        self.caller = caller
        self.serializer = serializer


    def do_request(self, url, data = None, method = None, empty_response = False):
        if data:
            data = self.serializer.serialize(data)

        if empty_response is True:
            return self.caller.do_request(url, data, method)

        return self.serializer.unserialize(self.caller.do_request(url, data, method))


    def download_request(self, url, dest, direct = False):
        if direct is True:
            return self.caller.download_request(url, dest)
        else:
            return self.caller.download_stream(url, dest)

