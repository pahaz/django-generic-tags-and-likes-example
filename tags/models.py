from __future__ import unicode_literals, print_function, generators, division
import logging
from core._six import text_type
from core.models import Slugged, Generalized
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet, Q, Count
from django.utils.translation import ugettext, ugettext_lazy as _
from core.utils import get_user_model_name
from django.db import models, connection
from tags.managers import TagManager
from tags.utils import parse_tag_input, join_tags

__author__ = 'pahaz'
user_model_name = get_user_model_name()
log = logging.getLogger(__name__)
qn = connection.ops.quote_name


class Tag(Slugged):
    objects = TagManager()

    class Meta:
        db_table = 'tags'
        unique_together = [('title', )]
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class TaggedItem(Generalized):
    tag = models.ForeignKey(Tag, verbose_name=_('Tag'), related_name='items')

    class Meta:
        db_table = 'tagged_items'
        unique_together = (
            ('content_type', 'object_id', 'tag'),
        )
        index_together = (
            ('content_type', 'tag'),
        )
        verbose_name = _('Tagged item')
        verbose_name_plural = _('Tagged items')


class TaggedModel(models.Model):
    tagged_items = GenericRelation(TaggedItem, editable=False)
    tags_string_cache = models.CharField(max_length=2000, blank=True,
                                         default='', editable=False)

    @classmethod
    def tagged_by_any(cls, tags, exclude_tags=None):
        tags = [x.pk for x in Tag.objects.get_or_create_list(tags)]
        if exclude_tags:
            exclude_tags = [x.pk for x in
                            Tag.objects.get_or_create_list(exclude_tags)]
        qs = cls.objects.all().annotate(ids=Count('id'))
        qs = qs.filter(Q(tagged_items__tag_id__in=tags) & Q(ids__gte=1))
        if exclude_tags:
            # TODO: FIX IT
            raise NotImplementedError
            # model = qn(cls._meta.db_table)
            # model_pk = qn(cls._meta.pk.column)
            # tagged = qn(TaggedItem._meta.db_table)
            # tagged_object_id = qn('object_id')
            # tagged_content_type_id = qn('content_type_id')
            # tagged_tag_id = qn('tag_id')
            # tags_ids = ', '.join(map(str, tags))
            # model_content_type_id = ContentType.objects.get_for_model(cls).pk
            # # SELECT U1."object_id" FROM tagged_items U1 WHERE
            # (U1."tag_id" IN (1) AND U1."content_type_id" = 4)
            # qs = qs.extra(where=["""
            # NOT ({model}.{model_pk} IN
            # (
            #     SELECT TAGGED1.{tagged_object_id} FROM {tagged} AS TAGGED1
            #     WHERE TAGGED1.{tagged_tag_id} IN ({tags_ids}) AND
            #        TAGGED1.{tagged_content_type_id} = {model_content_type_id}
            # ))
            # """.format(**locals())])

        # same with Q objects! TODO: test who faster :)
        # if tags:
        #     q = Q()
        #     for tag in tags:
        #         q &= Q(tagged_items__tag__title=tag)
        #     qs = cls.objects.filter(q)
        # else:
        #     qs = cls.objects.all()
        # if exclude_tags:
        #     for tag in exclude_tags:
        #         q &= ~Q(tagged_items__tag__title=tag)
        #     qs = cls.objects.exclude(q)

        return qs

    @classmethod
    def tagged_by_all(cls, tags, exclude_tags=None):
        tags = [x.pk for x in Tag.objects.get_or_create_list(tags)]
        if exclude_tags:
            exclude_tags = [x.pk for x in
                            Tag.objects.get_or_create_list(exclude_tags)]
        # tags = set(tags)
        # if exclude_tags:
        #     exclude_tags = set(exclude_tags)
        #     tags = tags - exclude_tags
        qs = cls.objects.all().annotate(ids=Count('id'))
        qs = qs.filter(Q(tagged_items__tag_id__in=tags) & Q(ids=len(tags)))
        if exclude_tags:
            # TODO: FIX IT
            raise NotImplementedError
            # q = q & (~Q(tagged_items__tag_id__in=exclude_tags))
        return qs

    def _get_tags(self):
        return self.tags_string_cache

    def _set_tags(self, value):
        if not isinstance(value, text_type):
            raise TypeError("Bad `value` type. Use text_type for assignment "
                            "the `tags` attribute")

        if self.pk is None:
            raise ValueError("Cannot assign tags to unsaved object. "
                             "Use .save() before assign tags.")

        value_tags = parse_tag_input(value)
        cleaned_value = join_tags(value_tags)

        new_tags = set(value_tags)
        current_tagged_items = self._get_tagged_items_query_set()
        current_tag_objs = [x.tag for x in current_tagged_items]
        current_tags = set(x.title for x in current_tag_objs)

        # check db state
        current_tags_cache = set(parse_tag_input(self.tags_string_cache))
        if current_tags != current_tags_cache:
            cls_name = type(self).__name__
            # TODO: think more about state desynchronization
            log.error("Found desynchronized db state. {0}.tags_string_cache "
                      "!= text representation of {0}.tagged_items.all(). "
                      "Used {0}.tagged_items.all() as true state and "
                      "{0}.tags_string_cache will be overwritten!"
                      .format(cls_name))
            self._update_tags_string_cache(current_tagged_items)
            self.save()

        if current_tags == new_tags:
            return

        new_tag_objs = Tag.objects.get_or_create_list(new_tags)
        new_tagged_items = [TaggedItem(tag_id=t.id) for t in new_tag_objs]

        self.tags_string_cache = cleaned_value
        setattr(self, 'tagged_items', new_tagged_items)
        self.save()
        # new_tag_ids = set(x.id for x in new_tag_objs)
        # current_tag_ids = set(x.id for x in current_tag_objs)
        # add_tags = new_tags - current_tags
        # delete_tags = Tag.objects.get_or_create_list(current_tags - new_tags)
        # Tag.objects.delete_unused(delete_tags)

    tags = property(_get_tags, _set_tags)

    def _update_tags_string_cache(self, tagged_items=None):
        if tagged_items is None:
            tagged_items = self._get_tagged_items_query_set()
        if not isinstance(tagged_items, QuerySet):
            raise TypeError('tagged_items is not a QuerySet instance')
        if isinstance(tagged_items.model, TaggedItem):
            raise TypeError('tagged_items.model is not a TaggedItem instance')
        self.tags_string_cache = ', '.join(x.tag.title for x in tagged_items)

    def _get_tagged_items_query_set(self):
        return self.tagged_items.all().select_related('tag')

    class Meta:
        abstract = True

