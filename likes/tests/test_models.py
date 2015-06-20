from __future__ import unicode_literals, print_function, generators, division
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.crypto import get_random_string
from likes.tests.models import Photo

__author__ = 'pahaz'


class TestLikedModel(TestCase):
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

    def get_photo_class(self):
        return Photo

    def make_unsaved_user(self, username=None):
        if username is None:
            username = get_random_string()
        user_model = get_user_model()
        return user_model(username=username)

    def make_user(self, username=None):
        if username is None:
            username = get_random_string()
        user_model = get_user_model()
        return user_model.objects.create(username=username)

    def assertLikedBy(self, obj, user):
        liked_count_cache = obj.liked_count_cache
        liked_count = obj._get_liked_items_query_set().count()
        liked_by_user = obj.is_liked_by(user)
        self.assertEqual(liked_count, liked_count_cache, 'Invalid cache')
        self.assertTrue(liked_by_user, 'No rel object')

    def assertDislikedBy(self, obj, user):
        liked_count_cache = obj.liked_count_cache
        liked_count = obj._get_liked_items_query_set().count()
        liked_by_user = obj.is_liked_by(user)
        self.assertEqual(liked_count, liked_count_cache, 'Invalid cache')
        self.assertFalse(liked_by_user, 'No rel object')

    def test_default_no_likes(self):
        p = self.make_photo()
        self.assertEqual(p.likes, 0)

    def test_simple_like_by(self):
        u = self.make_user()
        p = self.make_photo()
        p.like_by(u)
        self.assertLikedBy(p, u)

    def test_double_like_by(self):
        u = self.make_user()
        p = self.make_photo()
        is_liked = p.like_by(u)
        self.assertTrue(is_liked)
        is_liked = p.like_by(u)
        self.assertFalse(is_liked)
        self.assertLikedBy(p, u)

    def test_like_by_unsaved_user_raise_value_error(self):
        u = self.make_unsaved_user()
        p = self.make_photo()
        with self.assertRaises(ValueError):
            p.like_by(u)

    def test_like_by_stored_in_db(self):
        u = self.make_user()
        p = self.make_photo()
        p.like_by(u)
        p2 = self.get_photo(p.pk)
        self.assertLikedBy(p2, u)

    def test_dislike_by(self):
        u = self.make_user()
        p = self.make_photo()
        p.like_by(u)
        p2 = self.get_photo(p.pk)
        self.assertLikedBy(p2, u)
        p.dislike_by(u)
        p2 = self.get_photo(p.pk)
        self.assertDislikedBy(p2, u)

    def test_get_likes_require_0_queries(self):
        u = self.make_user()
        p = self.make_photo()
        p.like_by(u)
        with self.assertNumQueries(1):
            fp = self.get_photo(p.pk)
            self.assertEqual(fp.likes, 1)

    def test_like_unsaved_model_raise_value_error(self):
        u = self.make_user()
        p = self.make_unsaved_photo()
        with self.assertRaises(ValueError):
            p.like_by(u)

    def test_can_use_liked_items_in_queryset_filter(self):
        u1 = self.make_user()
        u2 = self.make_user()
        u_ids = [u1.id, u2.id]
        LIKED = self.filter_photo(liked_items__user_id__in=u_ids).distinct()
        self.assertEqual(LIKED.count(), 0)
        p1 = self.make_photo()
        p2 = self.make_photo()
        p1.like_by(u1)
        p1.like_by(u2)
        p2.like_by(u1)
        p2.like_by(u2)
        self.assertEqual(LIKED.count(), 2)

    def test_objects_liked_by(self):
        u1 = self.make_user()
        u2 = self.make_user()
        p1 = self.make_photo()
        p2 = self.make_photo()

        self.assertDislikedBy(p1, u1)
        self.assertDislikedBy(p1, u2)
        self.assertDislikedBy(p2, u1)
        self.assertDislikedBy(p2, u2)

        p1.like_by(u1)
        p2.like_by(u1)

        p12u1 = self.get_photo_class().objects_liked_by(u1)
        p12u2 = self.get_photo_class().objects_liked_by(u2)

        self.assertQuerysetEqual(p12u1.order_by('id'), map(repr, [p1, p2]))
        self.assertQuerysetEqual(p12u2.order_by('id'), map(repr, []))

        p1.like_by(u2)
        p2.like_by(u2)

        self.assertQuerysetEqual(p12u1.order_by('id'), map(repr, [p1, p2]))
        self.assertQuerysetEqual(p12u2.order_by('id'), map(repr, [p1, p2]))

        p1.dislike_by(u1)

        self.assertQuerysetEqual(p12u1.order_by('id'), map(repr, [p2]))
        self.assertQuerysetEqual(p12u2.order_by('id'), map(repr, [p1, p2]))
