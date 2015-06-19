from __future__ import unicode_literals, print_function, generators, division
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from tags.forms import TaggedModelForm
from tags.tests.models import Photo
from django.utils.crypto import get_random_string

__author__ = 'pahaz'


class PhotoTaggedForm(TaggedModelForm):

    class Meta:
        model = Photo
        exclude = tuple()


class TestTagsForm(TestCase):
    def setUp(self):
        ContentType.objects.get_for_model(Photo)  # warm cache

    def test_save_form(self):
        f = PhotoTaggedForm({'tags': 'Test1'})
        p = f.save()
        self.assertEqual(p.tags, "Test1")

    def test_save_form_without_tags_required_2_queries(self):
        f = PhotoTaggedForm({})
        with self.assertNumQueries(2 + 2):
            # 1st for insert
            # 2nd for check tags
            f.save()

    def test_save_form_with_1_tag_required_10_queries(self):
        RANDOM_TAG = get_random_string()
        f = PhotoTaggedForm({'tags': RANDOM_TAG})
        with self.assertNumQueries(10 + 2):
            # start transaction - (1)
            # insert object - (1)
            # select tagged items for object - (1)
            # get or create list of tags - (5) * len(tags)
            # (get, transaction begin, get, set, transaction begin) per tag
            # cleat all tagged items for object - (1)
            # insert new tagged items for object - (1) * len(tags)
            # update tag cache - (1)
            # end transaction - (1)
            # TODO: optimize get_or_create list of tags (-3 queries)
            p = f.save()
        self.assertEqual(p.tags, RANDOM_TAG)

    def test_save_form_with_2_tags_required_16_queries(self):
        RANDOM_TAG_1 = get_random_string()
        RANDOM_TAG_2 = get_random_string()
        TAGS = RANDOM_TAG_1 + ', ' + RANDOM_TAG_2
        f = PhotoTaggedForm({'tags': TAGS})
        with self.assertNumQueries(16 + 2):
            p = f.save()
        self.assertEqual(p.tags, TAGS)
