import requests

NEST_URL='https://www.inkpebble.com/comic/api/'

class Nest(object):
    auth = ()
    comic_list = 'list/'
    tag_list = 'tag/list/'
    tag_detail = 'tag/'
    panel_list = 'panel/list/'
    panel_detail = 'panel/'

    def __init__(self, url=NEST_URL, user=None, password=None):
        self.url = url
        if user and password:
           self.auth = (user, password)

    def get_comics(self):
        url = "%s%s" % (self.url, self.comic_list)
        if self.auth:
            return requests.get(url, auth=self.auth).json()
        return requests.get(url).json()

    def get_tags(self):
        url = "%s%s" % (self.url, self.tag_list)
        if self.auth:
            return requests.get(url, auth=self.auth).json()
        return requests.get(url).json()

    def get_panels(self):
        url = "%s%s" % (self.url, self.panel_list)
        if self.auth:
            return requests.get(url, auth=self.auth).json()
        return requests.get(url).json()

    def comic_detail(self, id):
        url = "%s%s/" % (self.url, id)
        if self.auth:
            return requests.get(url, auth=self.auth).json()
        return requests.get(url).json()

    def comic_save(self, id, data=None):
        if not self.auth:
            return {'error': 'You do not have permissions for that'}
        url = "%s%s/" % (self.url, id)
        r = requests.patch(url, data=data, auth=self.auth)
        return r.json()

    def tag_detail(self, id):
        url = "%s%s%s/" % (self.url, self.tag_detail, id)
        if self.auth:
            return requests.get(url, auth=self.auth).json()
        return requests.get(url).json()

    def tag_save(self, id, data=None):
        if not self.auth:
            return {'error': 'You do not have permissions for that'}
        url = "%s%s%s/" % (self.url, self.tag_detail, id)
        r = requests.patch(url, data=data, auth=self.auth)
        return r.json()

