from __future__ import unicode_literals, print_function, generators, division
from core.models import Owned, Slugged, Dated
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from likes.models import LikedModel
from tags.models import TaggedModel

__author__ = 'pahaz'

class Photo(LikedModel, TaggedModel, Owned, Slugged, Dated):
    url = models.URLField(verbose_name=_("Photo URL"))
    
    class Meta:
        db_table = "photo"
        verbose_name = _("Photo")
        verbose_name_plural = _("Photos")
