"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from rest_framework import routers

import views

router = routers.DefaultRouter()
router.register(r'registered_client', views.RegisteredClientViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^registered_client/$', views.RegisteredClientList.as_view(), name='registered_client'),
    url(r'^registered_clients/(?P<uuid>[0-9a-z-]+)/$', views.RegisteredClientDetail.as_view(),
        name='registered_clients'),
    url(r'^scores/registered_clients/(?P<uuid>[0-9a-z-]+)/$',
        views.ScoreList.as_view(), name='scores_for_client'),
    url(r'^scores/$', views.ScoreList.as_view(), name='scores')

]
