import factory

from pebbles import models


class PebbleFactory(factory.Factory):
    FACTORY_FOR = models.Pebble

    title = 'Test Pebble'