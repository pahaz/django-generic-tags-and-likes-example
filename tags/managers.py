from __future__ import unicode_literals, print_function, generators, division
import logging
from django.db import models

__author__ = 'pahaz'
log = logging.getLogger(__name__)


class TagManager(models.Manager):
    def delete_unused(self, tags=None):
        """
        Removes all instances that are not assigned to any object. Limits
        processing to ``tags_ids`` if given.
        """
        tags_ids = [x.id for x in tags] if tags else None
        tags = self.all() if tags_ids is None else self.filter(id__in=tags_ids)
        tags.filter(items__isnull=True).delete()

    def get_or_create_list(self, tags):
        result = []
        for tag in tags:
            obj, is_created = self.get_or_create(title=tag)
            result.append(obj)
        return result

    def get_list(self, tags):
        result = []
        for tag in tags:
            try:
                obj = self.get(title=tag)
            except self.model.DoesNotExist:
                obj = None
            except self.model.MultipleObjectsReturned:
                log.warning('Found desynchronized db state. Tag with title '
                            '"{0}" have multiple results.'.format(tag))
                obj = None
            result.append(obj)
        return result
