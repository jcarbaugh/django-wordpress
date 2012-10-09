from django.conf.urls.defaults import *

urlpatterns = patterns('wordpress.views',
    url(r'^author/(?P<username>\w+)/$', 'author_list', name='wp_author'),
    url(r'^category/(?P<term>[\w\-\./]+)/$', 'taxonomy', {'taxonomy': 'category'}, name='wp_taxonomy_category'),
    url(r'^tag/(?P<term>[\w\-\./]+)/$', 'taxonomy', {'taxonomy': 'term'}, name='wp_taxonomy_term'),
    url(r'^taxonomy/(?P<taxonomy>term|category)/(?P<term>[\w\-\./]+)/$', 'taxonomy', name='wp_taxonomy'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<post_slug>.+)/(?P<slug>.+)/$', 'object_attachment', name='wp_object_attachment'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>.+)/$', 'object_detail', name='wp_object_detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$', 'archive_day', name='wp_archive_day'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$', 'archive_month', name='wp_archive_month'),
    url(r'^(?P<year>\d{4})/$', 'archive_year', name='wp_archive_year'),
    url(r'^post/tag/(?P<term_slug>.+)/$', 'archive_term', name='wp_archive_term'),
    url(r'^$', 'archive_index', name='wp_archive_index'),
)