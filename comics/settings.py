from petroglyphs.models import Setting

def site_title():
    try:
        title = Setting.objects.get(key='site_title').value
    except Setting.DoesNotExist:
        title = 'Comics Site'
    return title

def site_url():
    try:
        url = Setting.objects.get(key='site_url').value
    except Setting.DoesNotExist:
        url = 'http://www.inkpebble.com'

    return url

def facebook_page_id():
    try:
        page_id = Setting.objects.get(key='facebook_page_id').value
    except Setting.DoesNotExist:
        page_id = ''

    return page_id

