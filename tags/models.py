from __future__ import unicode_literals, print_function, generators, division
from core._six import text_type
from core.models import Slugged, GenericItem
from django.contrib.contenttypes.generic import GenericRelation
from django.utils.translation import ugettext, ugettext_lazy as _
from core.utils import get_user_model_name
from django.db import models
from tags.managers import TagManager, TaggedModelManager

__author__ = 'pahaz'
user_model_name = get_user_model_name()


class Tag(Slugged):
    objects = TagManager()

    class Meta:
        db_table = 'tags'
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


class TaggedItem(GenericItem):
    tag = models.ForeignKey(Tag, verbose_name=_('Tag'), related_name='items')

    class Meta:
        db_table = 'tagged_items'
        unique_together = (('content_type', 'object_id', 'tag'), )
        verbose_name = _('Tagged item')
        verbose_name_plural = _('Tagged items')


class TaggedModel(models.Model):
    tags_relation = GenericRelation(TaggedItem, related_query_name='tags')
    tags_string = models.CharField(verbose_name=_('Tags'), max_length=2000)

    objects = models.Manager()
    tagged_objects = TaggedModelManager()

    def _get_tags(self):
        return self.tags_string

    def _set_tags(self, value):
        if isinstance(value, text_type):
            raise TypeError("Use text_type for assignment the `tags` attribute")

        if value == self.tags_string:
            return

        current_tags = self.tags_relation.all().select_telated('tag')
        tags = set([x.tag.name for x in current_tags])



    class Meta:
        abstract = True
