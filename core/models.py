from __future__ import unicode_literals, print_function, generators, division
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.six import python_2_unicode_compatible
from django.utils.translation import ugettext, ugettext_lazy as _
from core.utils import get_user_model_name, unique_slug
from django.db import models

__author__ = 'pahaz'
user_model_name = get_user_model_name()


class TimeStamped(models.Model):
    """
    Provides created and updated timestamps on models.
    """

    class Meta:
        abstract = True

    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)


class Ownable(models.Model):
    """
    Provides ownership of an object for a user.
    """

    user = models.ForeignKey(user_model_name, verbose_name=_("Author"),
        related_name="%(class)ss", editable=False)

    class Meta:
        abstract = True

    def is_editable(self, request):
        """
        Restrict editing to the objects's owner and superusers.
        """
        return request.user.is_superuser or request.user.id == self.user_id


@python_2_unicode_compatible
class Slugged(models.Model):
    """
    Provides auto-generating slugs.
    """

    title = models.CharField(_("Title"), max_length=500, unique=True,
                             db_index=True)
    slug = models.CharField(_("URL"), max_length=1000, blank=True, null=True,
            help_text=_("Leave blank to have the URL auto-generated from "
                        "the title."), db_index=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        If no slug is provided, generates one before saving.
        """
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super(Slugged, self).save(*args, **kwargs)

    def generate_unique_slug(self):
        """
        Create a unique slug by passing the result of get_slug() to
        utils.unique_slug, which appends an index if necessary.
        """
        slug_qs = self.objects.exclude(id=self.id)
        return unique_slug(slug_qs, "slug", self.get_slug())

    def get_slug(self):
        """
        Allows subclasses to implement their own slug creation logic.
        """
        slugged = self.title or ''
        if settings.USE_UNICODE_SLUGIFY:
            # https://pypi.python.org/pypi/unicode-slugify/0.1.3
            from slugify import slugify
            slugged = slugify(slugged)
        return slugged


class GenericItem(models.Model):
    object_id = models.IntegerField(verbose_name=_('Object id'), db_index=True)
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('Content type'),
        db_index=True
    )
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        index_together = ("content_type", "object_id")
        abstract = True
