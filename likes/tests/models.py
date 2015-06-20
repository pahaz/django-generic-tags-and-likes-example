from __future__ import unicode_literals, print_function, generators, division
from django.utils.six import python_2_unicode_compatible
from likes.models import LikedModel

__author__ = 'pahaz'


@python_2_unicode_compatible
class Photo(LikedModel):
    def __str__(self):
        return "{0}".format(self.pk)
