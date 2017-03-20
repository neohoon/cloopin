"""cloopin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.conf.urls import url
# from django.contrib import admin
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/foo/')),

    url(r'^foo', views.foo, name='foo'),
    url(r'^mygetview', views.my_get_view, name='my_get_view'),
    url(r'^mypostview', views.my_post_view, name='my_pos_tview'),
    url(r'^myajaxview', views.my_ajax_view, name='my_ajax_view'),
    url(r'^myajaxformview', views.my_ajax_form_view, name='my_ajax_form_view'),
    url(r'^myplay', views.play_audio_file, name='play_audio_file'),
]
