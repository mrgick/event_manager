import factory
from factory.django import DjangoModelFactory

from user.models import User


class UserFactory(DjangoModelFactory):
    email = factory.Sequence(lambda n: f'{n}@mail.org')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Sequence(lambda n: f'user_{n}')
    phone_number = factory.Sequence(lambda n: f'+7999{n:07d}')

    class Meta:
        model = User
