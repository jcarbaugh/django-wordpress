from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import list_detail, date_based
from wordpress.models import Post, Term
import datetime
import urllib

PER_PAGE = getattr(settings, 'WP_PER_PAGE', 10)

TAXONOMIES = {
    'term': 'post_tag',
    'category': 'category',
    'link_category': 'link_category',
}


def author_list(request, username):
    posts = Post.objects.published().filter(author__login=username)
    return list_detail.object_list(request, queryset=posts,
        paginate_by=PER_PAGE, template_name="wordpress/post_archive.html",
        template_object_name="post", allow_empty=True)


def preview(request, post_id):
    return list_detail.object_detail(
        request,
        queryset=Post.objects.all(),
        object_id=post_id,
        template_object_name='post',
        extra_context={
            'preview': True,
        }
    )


def object_detail(request, year, month, day, slug):
    slug = urllib.quote(slug.encode('utf-8')).lower()
    return date_based.object_detail(request, queryset=Post.objects.published(),
        date_field='post_date', year=year, month=month, month_format="%m",
        day=day, slug=slug, template_object_name='post', allow_future=True,
        extra_context={'post_url': request.build_absolute_uri(request.path)})


def object_attachment(request, year, month, day, post_slug, slug):
    post_date = datetime.datetime.strptime("%s/%s/%s" % (year, month, day), "%Y/%m/%d")
    post = get_object_or_404(Post.objects.published(),
        post_date__year=post_date.year,
        post_date__month=post_date.month,
        post_date__day=post_date.day,
        slug=urllib.quote(post_slug.encode('utf-8')).lower()
    )
    attachment = get_object_or_404(Post, post_type='attachment', slug=slug, parent=post)
    return HttpResponseRedirect(attachment.guid)


def archive_day(request, year, month, day):
    return date_based.archive_day(request, queryset=Post.objects.published(),
        date_field='post_date', year=year, month=month, month_format="%m",
        day=day, template_object_name='post')


def archive_month(request, year, month):
    return date_based.archive_month(request, queryset=Post.objects.published(),
        date_field='post_date', year=year, month=month, month_format="%m",
        template_object_name='post')


def archive_year(request, year):
    return date_based.archive_year(request, queryset=Post.objects.published(),
        date_field='post_date', year=year)


def archive_index(request):
    p = request.GET.get('p', None)
    if p:
        return preview(request, p)
    posts = Post.objects.published().select_related()
    return list_detail.object_list(request, queryset=posts,
        paginate_by=PER_PAGE, template_name='wordpress/post_archive.html',
        template_object_name='post', allow_empty=True)


def taxonomy(request, taxonomy, term):
    taxonomy = TAXONOMIES.get(taxonomy, None)
    if taxonomy:
        tag = Term.objects.get(slug=term)
        posts = Post.objects.term(tag.name, taxonomy=taxonomy).select_related()
        return list_detail.object_list(request, queryset=posts,
            paginate_by=PER_PAGE, template_name='wordpress/post_term.html',
            template_object_name='post', allow_empty=True,
            extra_context={"tag": tag, taxonomy: term})


def archive_term(request, term_slug):
    """
    List posts with common term.
    I am not going to implement this as I don't need it.
    This exists so I can generate URL stubs to the term archive.
    """
    pass
