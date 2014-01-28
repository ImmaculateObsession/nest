import factory

from pebbles import models


class PebbleFactory(factory.Factory):
    FACTORY_FOR = models.Pebble

    title = 'Test Pebble'

class PebbleSettingsFactory(factory.Factory):
    FACTORY_FOR = models.PebbleSettings

    settings = {'test':'test'}