from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve

import session_csrf
session_csrf.monkeypatch()

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:
    # url(r'^$', 'amazon_ranking.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^_ah/', include('djangae.urls')),

    # Note that by default this is also locked down with login:admin in app.yaml
    url(r'^admin/', include(admin.site.urls)),

    url(r'^csp/', include('cspreports.urls')),

    url(r'^auth/', include('djangae.contrib.gauth.urls')),
    url(r'^book/', include('book.urls')),
    url(r'^api/book/', include('book.api_urls')),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include('rest_framework_swagger.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, view=serve, show_indexes=True)
