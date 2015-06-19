from __future__ import unicode_literals, print_function, generators, division
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.crypto import get_random_string
from tags.models import Tag
from tags.tests.models import Photo

__author__ = 'pahaz'


class TestTagManager(TestCase):
    def setUp(self):
        ContentType.objects.get_for_model(Photo)  # warm cache

    def make_tag(self, title=None):
        if title is None:
            title = get_random_string()
        return Tag.objects.create(title=title)

    def filter_tags(self, **kwargs):
        return Tag.objects.filter(**kwargs)

    def assertNoTag(self, title):
        count_tags_with_title = self.filter_tags(title=title).count()
        self.assertEqual(count_tags_with_title, 0)

    def assertExistsTag(self, title):
        count_tags_with_title = self.filter_tags(title=title).count()
        self.assertEqual(count_tags_with_title, 1)

    def test_delete_unused(self):
        t = self.make_tag()
        t_title = t.title
        count_tags_with_t_title = self.filter_tags(title=t_title).count()
        self.assertEqual(count_tags_with_t_title, 1)

        Tag.objects.delete_unused()

        count_tags_with_t_title = self.filter_tags(title=t_title).count()
        self.assertEqual(count_tags_with_t_title, 0)

    def test_get_or_create_list(self):
        t1 = self.make_tag()
        t2 = self.make_tag()
        t3_title = get_random_string()

        self.assertExistsTag(t1.title)
        self.assertExistsTag(t2.title)
        self.assertNoTag(t3_title)

        tags = Tag.objects.get_or_create_list([t1.title, t2.title, t3_title])

        self.assertExistsTag(t1.title)
        self.assertExistsTag(t2.title)
        self.assertExistsTag(t3_title)

        self.assertEqual(tags[0].pk, t1.pk)
        self.assertEqual(tags[1].pk, t2.pk)
        self.assertEqual(tags[2].title, t3_title)
