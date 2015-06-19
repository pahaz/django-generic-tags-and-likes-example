from __future__ import unicode_literals, print_function, generators, division
import logging
from core._six import text_type
from core.models import Slugged, Generalized
from django.contrib.contenttypes.generic import GenericRelation
from django.db.models import QuerySet
from django.utils.translation import ugettext, ugettext_lazy as _
from core.utils import get_user_model_name
from django.db import models
from tags.managers import TagManager
from tags.utils import parse_tag_input, join_tags

__author__ = 'pahaz'
user_model_name = get_user_model_name()
log = logging.getLogger(__name__)


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
        unique_together = (('content_type', 'object_id', 'tag'), )
        verbose_name = _('Tagged item')
        verbose_name_plural = _('Tagged items')


class TaggedModel(models.Model):
    tagged_items = GenericRelation(TaggedItem, editable=False)
    tags_string_cache = models.CharField(max_length=2000, blank=True,
                                         default='', editable=False)

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

