import factory
from factory.django import DjangoModelFactory
from django.contrib.auth.models import User
from .models import Specialty, Doctor, ObsceneWord, ExceptionWord, Review
from django.contrib import messages


class SpecialtyFactory(DjangoModelFactory):
    class Meta:
        model = Specialty

    name = factory.Faker('job')


class DoctorFactory(DjangoModelFactory):
    class Meta:
        model = Doctor

    last_name = factory.Faker('last_name')
    name = factory.Faker('first_name')
    second_name = factory.Faker('last_name')


class ObsceneWordFactory(DjangoModelFactory):
    class Meta:
        model = ObsceneWord

    word = factory.Faker('word')


class ExceptionWordFactory(DjangoModelFactory):
    class Meta:
        model = ExceptionWord

    word = factory.Faker('word')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')


class ReviewFactory(DjangoModelFactory):
    class Meta:
        model = Review

    doctor = factory.SubFactory(DoctorFactory)
    original_text = factory.Faker('text', max_nb_chars=2000)
    processed_text = factory.LazyAttribute(lambda obj: obj.original_text)
    ip_address = factory.Faker('ipv4')
    user = factory.SubFactory(UserFactory)
