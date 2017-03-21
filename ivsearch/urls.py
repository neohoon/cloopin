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
from . import views

app_name = 'ivsearch'

urlpatterns = [
    url(r'^$', views.EntryView.as_view(), name='entry'),                            # None
    url(r'^entry/$', views.EntryView.as_view(), name='entry'),                      # entry
    url(r'^result/?$', views.ResultHsView.as_view(), name='result'),                # haystack_ result
    url(r'^detail/(?P<vid>[0-9]+)/$', views.DetailView.as_view(), name='detail'),    # detail/{$pk}
]


'''
app_name = 'ivsearch'

urlpatterns = [

    # url(r'^result/?$', views.ResultView.as_view(), name='result'),                      # result

    # url(r'^search/', include('haystack.urls')),
    # url(r'^search/?$', views.MySearchView.as_view(), name='my_search_view'),

    # url(r'^$', views.entry, name='entry'),                                # None
    # url(r'^entry/$', views.entry, name='entry'),                          # entry
    # url(r'^result/$', views.result, name='result'),                       # result
    # url(r'^detail/(?P<vid>[0-9]+)/$', views.detail, name='detail'),       # detail/{$pk}
]
'''