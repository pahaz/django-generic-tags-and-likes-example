from __future__ import unicode_literals, print_function, generators, division
from django.utils.six import python_2_unicode_compatible
from tags.models import TaggedModel

__author__ = 'pahaz'


@python_2_unicode_compatible
class Photo(TaggedModel):
    def __str__(self):
        return "{0}".format(self.pk)
