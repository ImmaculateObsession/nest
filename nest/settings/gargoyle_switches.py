SHOW_ADS = 'show_ads'
LIVE_COMIC_VIEW = 'live_comic_view'
COMIC_TAGGING = 'comic_tagging'
IMAGE_COMIC_NAV_BUTTONS = 'image_nav_buttons'

GARGOYLE_SWITCH_DEFAULTS = {
    SHOW_ADS: {
        'is_active': False,
        'label': 'Show ads on the site',
        'description': 'Whether or not ads are displayed.',
    },
    LIVE_COMIC_VIEW: {
        'is_active': False,
        'label': 'Enable the live comic view',
        'description': 'Enable a view that will use live tweets to create auto-updated comics',
    },
    COMIC_TAGGING: {
        'is_active': False,
        'label': 'Enable tagging for comics',
        'description': 'Show options on the comic add form for tagging',
    },
    IMAGE_COMIC_NAV_BUTTONS: {
        'is_active': False,
        'label': 'Image nav on comics',
        'description': 'Show large image nav buttons on comics',
    },
}