from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.googlemap, name='index'),
    url(r'^donate', views.donate, name='donate'),
    url(r'^queryLatlng', views.queryLatlng, name='donate')

]
