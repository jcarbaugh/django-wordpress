from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.views.generic import date_based
from wordpress.models import Post

TAXONOMIES = {
    'term': 'post_tag',
    'category': 'category',
    'link_category': 'link_category',
}
 
def object_detail(request, year, month, day, slug):
    return date_based.object_detail(request, queryset=Post.objects.published(),
        date_field='post_date', year=year, month=month, month_format="%m",
        day=day, slug=slug, slug_field='slug', template_object_name='post')
    
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
        post = Post.objects.get(pk=p)
        return HttpResponseRedirect(post.get_absolute_url())
    return date_based.archive_index(request,
        queryset=Post.objects.published(), date_field='post_date')

def taxonomy(request, taxonomy, term):
    taxonomy = TAXONOMIES.get(taxonomy, None)
    if taxonomy:
        posts = Post.objects.term(term, taxonomy=taxonomy)
        return render_to_response('wordpress/post_term.html', {'post_list': posts})