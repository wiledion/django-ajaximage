try:  # pre 1.6
    from django.conf.urls.defaults import url, patterns
except ImportError:
    from django.conf.urls import url  # after 1.8

from .views import ajaximage

urlpatterns =  [
    url(
        '^upload/(?P<upload_to>.*)/(?P<max_width>\d+)/(?P<max_height>\d+)/(?P<crop>\d+)/(?P<valid_width>\d+)/(?P<valid_height>\d+)/(?P<max_bytes>\d+)',
        ajaximage,
        name='ajaximage'
    ),
]
