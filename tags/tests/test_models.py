from __future__ import unicode_literals, print_function, generators, division
import unittest
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.crypto import get_random_string
from tags.tests.models import Photo
from tags.utils import parse_tag_input

__author__ = 'pahaz'


class TestTaggedModel(TestCase):
    def setUp(self):
        ContentType.objects.get_for_model(Photo)  # warm cache

    def make_photo(self, tags=None):
        p = Photo._default_manager.create()
        if tags:
            if isinstance(tags, (list, tuple)):
                tags = ', '.join(tags)
            p.tags = tags
        return p

    def make_unsaved_photo(self):
        return Photo()

    def get_photo_class(self):
        return Photo

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

    def assertNotTaggedBy(self, tag_title):
        tagged = self.filter_photo(tagged_items__tag__title=tag_title)
        self.assertEqual(tagged.count(), 0)

    def assertQueryResultEqual(self, qs, result, transform=repr):
        self.assertEqual(set(map(transform, qs)),
                         set(map(transform, result)))

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
        self.make_photo([TAG_BLACK, TAG_RETRO])
        self.make_photo([TAG_BLACK])
        self.assertEqual(TAGGED_BLACK.count(), 2)
        self.assertEqual(TAGGED_RETRO.count(), 1)

    def test_objects_tagged_by_any(self):
        TAG_BLACK = "Black" + get_random_string()
        TAG_RETRO = "Retro" + get_random_string()
        TAG_VINTAGE = "Vintage" + get_random_string()

        self.assertNotTaggedBy(TAG_BLACK)
        self.assertNotTaggedBy(TAG_RETRO)
        self.assertNotTaggedBy(TAG_VINTAGE)

        p1 = self.make_photo([TAG_BLACK, TAG_RETRO])
        p2 = self.make_photo([TAG_BLACK, TAG_VINTAGE])

        bvr = p1.objects_tagged_by_any([TAG_BLACK, TAG_VINTAGE, TAG_RETRO])
        print("\n_ANY_bvr_", bvr.query)
        self.assertQueryResultEqual(bvr, [p1, p2])

        bv = p1.objects_tagged_by_any([TAG_BLACK, TAG_VINTAGE])
        print("\n_ANY_bv_", bv.query)
        self.assertQueryResultEqual(bv, [p1, p2])

    @unittest.skip("Not implemented")
    def test_objects_tagged_by_any_with_exclude(self):
        TAG_BLACK = "Black" + get_random_string()
        TAG_RETRO = "Retro" + get_random_string()
        TAG_VINTAGE = "Vintage" + get_random_string()

        self.assertNotTaggedBy(TAG_BLACK)
        self.assertNotTaggedBy(TAG_RETRO)
        self.assertNotTaggedBy(TAG_VINTAGE)

        p1 = self.make_photo([TAG_BLACK, TAG_RETRO])
        p2 = self.make_photo([TAG_BLACK, TAG_VINTAGE])

        bvNr = p1.objects_tagged_by_any([TAG_BLACK, TAG_VINTAGE], [TAG_RETRO])
        print("\n_ANY_bvNr_", bvNr.query)
        self.assertQueryResultEqual(bvNr, [p2])

        bNvNr = p1.objects_tagged_by_any([TAG_BLACK, TAG_RETRO, TAG_VINTAGE],
                                         [TAG_RETRO, TAG_VINTAGE])
        print("\n_ANY_bNvNr_", bNvNr.query)
        self.assertQueryResultEqual(bNvNr, [])

    def test_objects_tagged_by_all(self):
        TAG_BLACK = "Black" + get_random_string()
        TAG_RETRO = "Retro" + get_random_string()
        TAG_VINTAGE = "Vintage" + get_random_string()

        self.assertNotTaggedBy(TAG_BLACK)
        self.assertNotTaggedBy(TAG_RETRO)
        self.assertNotTaggedBy(TAG_VINTAGE)

        p1 = self.make_photo([TAG_BLACK, TAG_RETRO])
        p2 = self.make_photo([TAG_BLACK, TAG_VINTAGE])

        bvr = p1.objects_tagged_by_all([TAG_BLACK, TAG_VINTAGE, TAG_RETRO])
        print("\n_ALL_bvr_", bvr.query)
        self.assertQueryResultEqual(bvr, [])

        bv = p1.objects_tagged_by_all([TAG_BLACK, TAG_VINTAGE])
        print("\n_ALL_bv_", bv.query)
        self.assertQueryResultEqual(bv, [p2])

    # @unittest.skip("Not implemented")
    def test_objects_tagged_by_all_with_exclude(self):
        TAG_BLACK = "Black" + get_random_string()
        TAG_RETRO = "Retro" + get_random_string()
        TAG_VINTAGE = "Vintage" + get_random_string()

        self.assertNotTaggedBy(TAG_BLACK)
        self.assertNotTaggedBy(TAG_RETRO)
        self.assertNotTaggedBy(TAG_VINTAGE)

        p1 = self.make_photo([TAG_BLACK, TAG_RETRO])
        p2 = self.make_photo([TAG_BLACK, TAG_VINTAGE])

        bvNr = p1.objects_tagged_by_all([TAG_BLACK, TAG_VINTAGE], [TAG_RETRO])
        print("\n_ALL_bvNr_", bvNr.query)
        self.assertQueryResultEqual(bvNr, [p2])

        bNvNr = p1.objects_tagged_by_all([TAG_BLACK, TAG_RETRO, TAG_VINTAGE],
                                         [TAG_RETRO, TAG_VINTAGE])
        print("\n_ALL_bNvNr_", bNvNr.query)
        self.assertQueryResultEqual(bNvNr, [])

    def test_objects_tagged_by_all_with_exclude_complex(self):
        TAG_BLACK = "Black" + get_random_string()
        TAG_RETRO = "Retro" + get_random_string()
        TAG_VINTAGE = "Vintage" + get_random_string()
        Photo = self.get_photo_class()

        self.assertNotTaggedBy(TAG_BLACK)
        self.assertNotTaggedBy(TAG_RETRO)
        self.assertNotTaggedBy(TAG_VINTAGE)

        p0 = self.make_photo([TAG_VINTAGE, TAG_RETRO])
        p1 = self.make_photo([TAG_BLACK, TAG_RETRO])
        p2 = self.make_photo([TAG_BLACK, TAG_VINTAGE])
        p3 = self.make_photo([TAG_BLACK])
        p4 = self.make_photo([TAG_BLACK, TAG_RETRO, TAG_VINTAGE])
        p5 = self.make_photo([TAG_RETRO])
        p6 = self.make_photo([TAG_VINTAGE])

        _p1 = Photo.objects_tagged_by_all([TAG_BLACK, TAG_RETRO],
                                          [TAG_VINTAGE])
        self.assertQueryResultEqual(_p1, [p1])

        _p3 = Photo.objects_tagged_by_all([TAG_BLACK],
                                          [TAG_VINTAGE, TAG_RETRO])
        self.assertQueryResultEqual(_p3, [p3])

        _p1_p5 = Photo.objects_tagged_by_all([TAG_RETRO], [TAG_VINTAGE])
        self.assertQueryResultEqual(_p1_p5, [p1, p5])

        _p4 = Photo.objects_tagged_by_all([TAG_BLACK, TAG_RETRO, TAG_VINTAGE])
        self.assertQueryResultEqual(_p4, [p4])

        _p2_p6 = Photo.objects_tagged_by_all([TAG_VINTAGE], [TAG_RETRO])
        self.assertQueryResultEqual(_p2_p6, [p2, p6])

        _p0_p6 = Photo.objects_tagged_by_all([TAG_VINTAGE], [TAG_BLACK])
        self.assertQueryResultEqual(_p0_p6, [p0, p6])

    def test_objects_tagged_by_any_with_exclude_complex(self):
        TAG_BLACK = "Black" + get_random_string()
        TAG_RETRO = "Retro" + get_random_string()
        TAG_VINTAGE = "Vintage" + get_random_string()
        Photo = self.get_photo_class()

        self.assertNotTaggedBy(TAG_BLACK)
        self.assertNotTaggedBy(TAG_RETRO)
        self.assertNotTaggedBy(TAG_VINTAGE)

        p0 = self.make_photo([TAG_VINTAGE, TAG_RETRO])
        p1 = self.make_photo([TAG_BLACK, TAG_RETRO])
        p2 = self.make_photo([TAG_BLACK, TAG_VINTAGE])
        p3 = self.make_photo([TAG_BLACK])
        p4 = self.make_photo([TAG_BLACK, TAG_RETRO, TAG_VINTAGE])
        p5 = self.make_photo([TAG_RETRO])
        p6 = self.make_photo([TAG_VINTAGE])

        _nB = Photo.objects_tagged_by_any([TAG_BLACK, TAG_RETRO, TAG_VINTAGE],
                                          [TAG_BLACK])
        self.assertQueryResultEqual(_nB, [p0, p5, p6])

        _nV = Photo.objects_tagged_by_any([TAG_BLACK, TAG_RETRO, TAG_VINTAGE],
                                          [TAG_VINTAGE])
        self.assertQueryResultEqual(_nV, [p1, p3, p5])

        _nRV = Photo.objects_tagged_by_any([TAG_BLACK, TAG_RETRO, TAG_VINTAGE],
                                           [TAG_RETRO, TAG_VINTAGE])
        self.assertQueryResultEqual(_nRV, [p3])

        _p1_p3_p5 = Photo.objects_tagged_by_any([TAG_BLACK, TAG_RETRO],
                                                [TAG_VINTAGE])
        self.assertQueryResultEqual(_p1_p3_p5, [p1, p3, p5])

        _p3 = Photo.objects_tagged_by_any([TAG_BLACK],
                                          [TAG_VINTAGE, TAG_RETRO])
        self.assertQueryResultEqual(_p3, [p3])

        _p1_p5 = Photo.objects_tagged_by_any([TAG_RETRO], [TAG_VINTAGE])
        self.assertQueryResultEqual(_p1_p5, [p1, p5])

        _p_all = Photo.objects_tagged_by_any(
            [TAG_BLACK, TAG_RETRO, TAG_VINTAGE])
        self.assertQueryResultEqual(_p_all, [p0, p1, p2, p3, p4, p5, p6])

        _p2_p6 = Photo.objects_tagged_by_any([TAG_VINTAGE], [TAG_RETRO])
        self.assertQueryResultEqual(_p2_p6, [p2, p6])

        _p0_p6 = Photo.objects_tagged_by_any([TAG_VINTAGE], [TAG_BLACK])
        self.assertQueryResultEqual(_p0_p6, [p0, p6])
