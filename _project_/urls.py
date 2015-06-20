from django.conf.urls import include, url
from django.contrib import admin
from photos.view import PhotoListView

urlpatterns = [
    # Examples:
    # url(r'^$', 'PhotoServer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^photos/', include('photos.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
