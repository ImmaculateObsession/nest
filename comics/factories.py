import factory

from django.contrib.auth.models import User
from comics import models


class UserFactory(factory.Factory):
    FACTORY_FOR = User

    first_name = "Testy"
    last_name = "McTesterson"
    email = "test@example.com"


class PostFactory(factory.Factory):
    FACTORY_FOR = models.Post

    title = factory.Sequence(lambda n: 'Test Comic %d' % n)
    post = 'This is a test of the post model'
    slug = 'this-is-a-test'
    creator = factory.SubFactory(UserFactory)


class ComicFactory(factory.Factory):
    FACTORY_FOR = models.Comic

    title = factory.Sequence(lambda n: 'Test Comic %d' % n) 
    image_url = "http://media.examples.com/test.png"
    creator = factory.SubFactory(UserFactory)
    post = factory.SubFactory(PostFactory)





