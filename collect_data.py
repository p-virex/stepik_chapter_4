import os
import json


class CollectData:
    def __init__(self):
        self.DATA_FILE = os.path.join(os.getcwd(), 'data', 'data.json')
        self.BOOKING_FILE = os.path.join(os.getcwd(), 'data', 'booking.json')
        self.REQUEST_FILE = os.path.join(os.getcwd(), 'data', 'request.json')
        self.data = dict()
        self.booking = dict()
        self.request = dict()

    def set_to_data(self, key, value, name='data'):
        getattr(self, name).update({key: value})
        self.write_data(name)

    def get_from_data(self, key, name='data'):
        return getattr(self, name).get(key)

    def write_data(self, name):
        to_file = getattr(self, '{}_FILE'.format(name.upper()))
        json.dump(getattr(self, name), open(to_file, 'w'), indent=4)

    @property
    def get_data(self, name='data'):
        return getattr(self, name)


g_data = CollectData()
