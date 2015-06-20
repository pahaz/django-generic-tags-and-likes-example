from __future__ import unicode_literals, print_function, generators, division
import logging
from core._six import text_type
from core.models import Generalized, Owned
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.utils.translation import ugettext, ugettext_lazy as _
from core.utils import get_user_model_name
from django.db import models
from django.db.models import F

__author__ = 'pahaz'
user_model_name = get_user_model_name()
user_model = None
log = logging.getLogger(__name__)


class LikedItem(Owned, Generalized):

    class Meta:
        db_table = 'liked_items'
        index_together = (
            ('content_type', 'object_id', 'user'),
            ('content_type', 'user'),
        )
        unique_together = (('content_type', 'object_id', 'user'), )
        verbose_name = _('Liked item')
        verbose_name_plural = _('Liked items')


class LikedModel(models.Model):
    liked_items = GenericRelation(LikedItem, editable=False)
    liked_count_cache = models.IntegerField(default=0, editable=False,
                                            db_index=True)

    @classmethod
    def objects_liked_by(cls, user):
        cls._check_user_model(user, 'like_by')
        return cls.objects.filter(liked_items__user_id=user.id)

    def like_by(self, user):
        """
        Like model object by user.

        :param user: User instance
        :return: False if like by user exists else True
        """
        self._check_user_model(user, 'like_by')
        self._check_model_has_pk('like_by')
        like, created = self._get_liked_items_query_set().get_or_create(
            user_id=user.pk)
        if created:
            self._change_cache_value(+1)
        return created

    def dislike_by(self, user):
        self._check_user_model(user, 'dislike_by')
        self._check_model_has_pk('dislike_by')
        if self.is_liked_by(user):
            self._get_liked_items_query_set(user_id=user.pk).delete()
            self._change_cache_value(-1)
            return True
        return False

    def is_liked_by(self, user):
        self._check_user_model(user, 'is_liked_by')
        self._check_model_has_pk('is_liked_by')

        try:
            self._get_liked_items_query_set().get(user_id=user.pk)
            return True
        except LikedItem.DoesNotExist:
            return False

    @property
    def likes(self):
        return self.liked_count_cache

    def _get_liked_items_query_set(self, **kwargs):
        qs = self.liked_items if not kwargs else \
            self.liked_items.filter(**kwargs)
        return qs

    @classmethod
    def _check_user_model(cls, user, for_method):
        global user_model
        if user_model is None:
            user_model = get_user_model()
        if not isinstance(user, user_model):
            raise TypeError('Use {0}.{1}(user) with not a user instance'
                            .format(cls.__name__, for_method))
        if user.pk is None:
            raise ValueError("Cannot assign like to unsaved user object. "
                             "Use user.save() before .{0}(user)."
                             .format(for_method))

    def _check_model_has_pk(self, for_method):
        if self.pk is None:
            raise ValueError("Cannot like to unsaved object. "
                             "Use .save() before {0}.".format(for_method))

    def _change_cache_value(self, value):
        type(self).objects.filter(pk=self.pk).update(
            liked_count_cache=F('liked_count_cache') + value)
        self.refresh_from_db(fields=['liked_count_cache'])

    class Meta:
        abstract = True

