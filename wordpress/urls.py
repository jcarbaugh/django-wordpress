from django.conf.urls.defaults import *

urlpatterns = patterns('wordpress.views',
    url(r'^author/(?P<username>\w+)/$', 'author_list', name='wp_author'),
    url(r'^taxonomy/(?P<taxonomy>term|category)/(?P<term>[\w\-\./]+)/$', 'taxonomy', name='wp_taxonomy'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>.+)/$', 'object_detail', name='wp_object_detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'archive_day', name='wp_archive_day'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'archive_month', name='wp_archive_month'),
    url(r'^(?P<year>\d{4})/$', 'archive_year', name='wp_archive_year'),
    url(r'^$', 'archive_index', name='wp_archive_index'),
)