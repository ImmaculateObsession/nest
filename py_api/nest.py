import requests

NEST_URL='http://localhost:8000/comic/api/'

class Nest(object):
    auth = {}
    comic_list = 'list/'
    tag_list = 'tag/list/'
    tag_detail = 'tag/'
    panel_list = 'panel/list/'
    panel_detail = 'panel/'

    def __init__(self, url=NEST_URL, user=None, password=None):
        self.url = url
        if user:
            self.auth['user'] = user
        if password:
            self.auth['password'] = password

    def get_comics(self):
        url = "%s%s" % (self.url, self.comic_list)
        r = requests.get(url)
        return r.json()

    def get_tags(self):
        url = "%s%s" % (self.url, self.tag_list)
        r = requests.get(url)
        return r.json()

    def get_panels(self):
        url = "%s%s" % (self.url, self.panel_list)
        r = requests.get(url)
        return r.json()

    def comic_detail(self, id):
        url = "%s%s/" % (self.url, id)
        r = requests.get(url)
        return r.json()

    def comic_save(self, id, data=None):
        if not self.auth or not self.auth.get('user') or not self.auth.get('password'):
            return {'error': 'You do not have permissions for that'}
        url = "%s%s/" % (self.url, id)
        auth_tuple = (self.auth['user'], self.auth['password'])
        r = requests.patch(url, data=data, auth=auth_tuple)
        return r.json()

