from __future__ import unicode_literals, print_function, generators, division
from django.views.generic import ListView
from photos.models import Photo
from tags.models import Tag

__author__ = 'pahaz'


class PhotoListView(ListView):
    queryset = Photo.objects.all()
    context_object_name = 'photos'
    template_name = 'photo_list.html'
    paginate_by = 20

    def get_queryset(self):
        tags = self.kwargs.get('tags')
        if tags:
            tags = tags.split('~')
            if len(tags) == 1:
                return self.queryset.filter(tagged_items__tag__slug=tags[0])
            else:
                return self.queryset.filter(tagged_items__tag__slug__in=tags)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(PhotoListView, self).get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        return context
