from __future__ import unicode_literals, print_function, generators, division
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.crypto import get_random_string
from tags.tests.models import Photo
from tags.utils import parse_tag_input

__author__ = 'pahaz'


class TestTaggedModel(TestCase):
    def setUp(self):
        ContentType.objects.get_for_model(Photo)  # warm cache

    def make_photo(self):
        return Photo._default_manager.create()

    def make_unsaved_photo(self):
        return Photo()

    def filter_photo(self, **kwargs):
        return Photo.objects.filter(**kwargs)

    def get_photo(self, pk):
        return Photo.objects.get(pk=pk)

    def assertTags(self, obj, expected_tags_string):
        expected_tags = set(parse_tag_input(expected_tags_string))
        current_tags_cache = set(parse_tag_input(obj.tags_string_cache))
        current_tags = set(x.tag.title for x in
                           obj._get_tagged_items_query_set())
        self.assertEqual(expected_tags, current_tags_cache, 'Invalid cache')
        self.assertEqual(expected_tags, current_tags, 'Invalid rel objects')

    def test_default_no_tags(self):
        p = self.make_photo()
        self.assertEqual(p.tags, "")

    def test_simple_set_tags(self):
        TAGS = "Black, Retro"
        p = self.make_photo()
        p.tags = TAGS
        self.assertTags(p, TAGS)

    def test_set_tags_stored_in_db(self):
        TAGS = "Black, Retro"
        p = self.make_photo()
        p.tags = TAGS
        p2 = self.get_photo(p.pk)
        self.assertTags(p2, TAGS)

    def test_set_tags_overwrite_old_tags(self):
        TAGS1 = "Black, Retro"
        TAGS2 = "White, Vintage"
        p = self.make_photo()
        p.tags = TAGS1
        self.assertTags(p, TAGS1)
        p.tags = TAGS2
        self.assertTags(p, TAGS2)

    def test_get_tags_require_0_queries(self):
        TAGS = "Black, Retro"
        p = self.make_photo()
        p.tags = TAGS
        with self.assertNumQueries(1):
            fp = self.get_photo(p.pk)
            self.assertEqual(fp.tags, TAGS)

    def test_set_tags_to_unsaved_model_raise_value_error(self):
        TAGS = "Black, Retro"
        p = self.make_unsaved_photo()
        with self.assertRaises(ValueError):
            p.tags = TAGS

    def test_can_use_tagged_items_in_queryset_filter(self):
        TAG_BLACK = "Black" + get_random_string()
        TAG_RETRO = "Retro" + get_random_string()
        TAGGED_BLACK = self.filter_photo(tagged_items__tag__title=TAG_BLACK)
        TAGGED_RETRO = self.filter_photo(tagged_items__tag__title=TAG_RETRO)
        self.assertEqual(TAGGED_BLACK.count(), 0)
        self.assertEqual(TAGGED_RETRO.count(), 0)
        p1 = self.make_photo()
        p1.tags = TAG_BLACK + ', ' + TAG_RETRO
        p2 = self.make_photo()
        p2.tags = TAG_BLACK
        self.assertEqual(TAGGED_BLACK.count(), 2)
        self.assertEqual(TAGGED_RETRO.count(), 1)
