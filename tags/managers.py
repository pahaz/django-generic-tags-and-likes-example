from __future__ import unicode_literals, print_function, generators, division
from django.db import models

__author__ = 'pahaz'


class TagManager(models.Manager):
    def delete_unused(self, keyword_ids=None):
        """
        Removes all instances that are not assigned to any object. Limits
        processing to ``keyword_ids`` if given.
        """
        if keyword_ids is None:
            keywords = self.all()
        else:
            keywords = self.filter(id__in=keyword_ids)
        keywords.filter(assignments__isnull=True).delete()


class TaggedModelManager(models.Manager):
    pass
