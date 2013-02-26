from django.conf.urls import *
from wordpress.views import *

urlpatterns = patterns('wordpress.views',

    url(r'^author/(?P<username>\w+)/$',
        AuthorArchive.as_view(), name='wp_author'),

    url(r'^category/(?P<term>.+)/$',
        TaxonomyArchive.as_view(), {'taxonomy': 'category'}, name='wp_taxonomy_category'),
    url(r'^tag/(?P<term>.+)/$',
        TaxonomyArchive.as_view(), {'taxonomy': 'term'}, name='wp_taxonomy_term'),
    url(r'^taxonomy/(?P<taxonomy>term|category)/(?P<term>.+)/$',
        TaxonomyArchive.as_view(), name='wp_taxonomy'),

    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[^/]+)/(?P<attachment_slug>[^/]+)/$',
        PostAttachment.as_view(), name='wp_object_attachment'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<slug>[^/]+)/$',
        PostDetail.as_view(), name='wp_object_detail'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})/$',
        DayArchive.as_view(), name='wp_archive_day'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        MonthArchive.as_view(), name='wp_archive_month'),
    url(r'^(?P<year>\d{4})/$',
        YearArchive.as_view(), name='wp_archive_year'),

    url(r'^post/tag/(?P<term_slug>.+)/$',
        TermArchive.as_view(), name='wp_archive_term'),
    url(r'^$',
        Archive.as_view(), name='wp_archive_index'),

)
