from __future__ import unicode_literals, print_function, generators, division
import logging
from core._six import text_type
from core.models import Slugged, Generalized
from django.contrib.contenttypes.fields import GenericRelation
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
        unique_together = [('title',)]
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
    def objects_tagged_by_any(cls, tags, exclude_tags=None):
        tags = [x.pk for x in Tag.objects.get_list(tags) if x]
        if exclude_tags:
            exclude_tags = Tag.objects.get_list(exclude_tags)
            exclude_tags = [x.pk for x in exclude_tags if x]

        qs = cls.objects.annotate(ids=Count('id'))
        q = Q(tagged_items__tag_id__in=tags) & Q(ids__gte=1)
        if exclude_tags:
            model_content_type = ContentType.objects.get_for_model(cls).pk
            exclude_object_ids = TaggedItem.objects.filter(
                tag_id__in=exclude_tags, content_type=model_content_type) \
                .values('object_id')
            q &= ~Q(id__in=exclude_object_ids)

        return qs.filter(q)

    @classmethod
    def objects_tagged_by_all(cls, tags, exclude_tags=None):
        tags = Tag.objects.get_list(tags)
        if any(x is None for x in tags):
            return cls.objects.none()
        tags = [x.pk for x in tags]
        if exclude_tags:
            exclude_tags = Tag.objects.get_list(exclude_tags)
            exclude_tags = [x.pk for x in exclude_tags if x]

        qs = cls.objects.annotate(ids=Count('id'))
        q = Q(tagged_items__tag_id__in=tags) & Q(ids=len(tags))
        if exclude_tags:
            model_content_type = ContentType.objects.get_for_model(cls).pk
            exclude_object_ids = TaggedItem.objects.filter(
                tag_id__in=exclude_tags, content_type=model_content_type) \
                .values('object_id')
            q &= ~Q(id__in=exclude_object_ids)

        return qs.filter(q)

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

    def _get_tagged_items_query_set(self, **kwargs):
        qs = self.tagged_items if not kwargs else \
            self.tagged_items.filter(**kwargs)
        return qs.select_related('tag')

    class Meta:
        abstract = True
