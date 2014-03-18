SHOW_ADS = 'show_ads'
LIVE_COMIC_VIEW = 'live_comic_view'

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
}