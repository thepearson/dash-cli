from json import dumps, loads

class JsonSeriaizer():

    def serialize(self, data):
        return dumps(data)

    def unserialize(self, string):
        return loads(string)
