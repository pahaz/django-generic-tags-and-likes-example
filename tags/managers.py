from __future__ import unicode_literals, print_function, generators, division
from django.db import models

__author__ = 'pahaz'


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
