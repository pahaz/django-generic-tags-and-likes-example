from django.conf.urls import url
from photos.view import PhotoListView

urlpatterns = [
    url(r'^$', PhotoListView.as_view(), name="photos_index"),
    url(r'^(?P<tags>[a-z0-9-]+(~[a-z0-9-]+)*)/$', PhotoListView.as_view(),
        name="photos_tagged"),
]
