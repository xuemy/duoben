from django.conf import settings
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'duoben.views.home', name='home'),
                       # url(r'^blog/', include('blog.urls')),


                       url(r'^comments/', include('django.contrib.comments.urls')),
                       url(r"^$", "app.views.index", name="index"),
                       url(r'^(?P<slug>[A-Za-z]+)$', "app.views.novel", name="novel"),
                       url(r'^(?P<slug>[A-Za-z]+)/(?P<cid>\d+)$', "app.views.chapter", name="chapter"),
)

if settings.DEBUG:
    urlpatterns += patterns("",
                            url(r"^media/(?P<path>.*)$", \
                                "django.views.static.serve", \
                                {"document_root": settings.MEDIA_ROOT, }))


if settings.DEBUG:
    urlpatterns += patterns("",url(r'^admin/', include(admin.site.urls)),)
else:
    from local_settings import local_url
    urlpatterns += local_url