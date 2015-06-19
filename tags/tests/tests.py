from __future__ import unicode_literals, print_function, generators, division
from django.test import TestCase
from tags.tests.models import Photo

__author__ = 'pahaz'


class TestTaggedModelManager(TestCase):
    def make_photo(self):
        return Photo._default_manager.create()

    def test_no_tags(self):
        p = self.make_photo()
        p.tags.all()
