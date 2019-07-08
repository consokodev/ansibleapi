"""ansibleapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from ansibleapi.views import api_return_error
from api import views as v1

urlpatterns = (
    url(r'projects/$', v1.ProjectViewSet.as_view()),
    url(r'projects/(?P<pk>[0-9]+)/execute-module-api/$', v1.ProjectExecuteCommandSet.as_view()),
    url(r'history/(?P<pk>[0-9]+)/raw/$', v1.HistoryViewRawSet.as_view()),
    url(r'history/(?P<pk>[0-9]+)/$', v1.HistoryViewSet.as_view()),
)
