from __future__ import unicode_literals, print_function, generators, division
import os

__author__ = 'pahaz'
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, '__data__')

SECRET_KEY = 'fake-key'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(DATA_DIR, 'db.test.sqlite3'),
    }
}
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "likes",
    "likes.tests",
]
