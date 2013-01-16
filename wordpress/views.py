from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views import generic
from wordpress.models import Post, Term
import urllib

PER_PAGE = getattr(settings, 'WP_PER_PAGE', 10)

TAXONOMIES = {
    'term': 'post_tag',
    'category': 'category',
    'link_category': 'link_category',
}


class AuthorArchive(generic.list.ListView):

    allow_empty = True
    context_object_name = "post_list"
    paginate_by = PER_PAGE
    template_name = "wordpress/post_archive.html"

    def get_queryset(self):
        return Post.objects.published().filter(author__login=self.kwargs['username'])


class Preview(generic.detail.DetailView):

    context_object_name = 'post'
    pk_url_kwarg = 'p'
    queryset = Post.objects.all()

    def get_context_data(self, **kwargs):
        context = super(Preview, self).get_context_data(**kwargs)
        context.update({'preview': True})
        return context


class PostDetail(generic.dates.DateDetailView):

    allow_future = True
    context_object_name = 'post'
    date_field = 'post_date'
    month_format = "%m"
    queryset = Post.objects.published()

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data(**kwargs)
        context.update({'post_url': self.request.build_absolute_uri(self.request.path)})
        return context

    def get_object(self):
        self.kwargs['slug'] = urllib.quote(self.kwargs['slug'].encode('utf-8')).lower()
        return super(PostDetail, self).get_object()

    def get(self, request, *args, **kwargs):
        return super(PostDetail, self).get(request, *args, **kwargs)


class PostAttachment(PostDetail):

    def get(self, request, *args, **kwargs):
        post = self.get_object()
        attachment = get_object_or_404(Post, post_type='attachment', slug=self.kwargs['attachment_slug'], parent=post)
        return HttpResponseRedirect(attachment.guid)


class DayArchive(generic.dates.DayArchiveView):
    context_object_name = 'post_list'
    date_field = 'post_date'
    month_format = '%m'
    paginate_by = PER_PAGE
    queryset = Post.objects.published()


class MonthArchive(generic.dates.MonthArchiveView):
    context_object_name = 'post_list'
    date_field = 'post_date'
    month_format = '%m'
    paginate_by = PER_PAGE
    queryset = Post.objects.published()


class YearArchive(generic.dates.YearArchiveView):
    context_object_name = 'post_list'
    date_field = 'post_date'
    paginate_by = PER_PAGE
    queryset = Post.objects.published()


class Archive(generic.dates.ArchiveIndexView):

    allow_empty = True
    context_object_name = 'post_list'
    paginate_by = PER_PAGE
    template_name = 'wordpress/post_archive.html'

    def get(self, request, *args, **kwargs):
        p = request.GET.get('p', None)
        if p:
            return Preview.as_view()(request)
        return super(Archive, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return Post.objects.published().select_related()


class TaxonomyArchive(generic.list.ListView):

    allow_empty = True
    context_object_name = "post_list"
    paginate_by = PER_PAGE
    template_name = "wordpress/post_term.html"

    def get_context_data(self, **kwargs):
        context = super(TaxonomyArchive, self).get_context_data(**kwargs)
        context.update({
            'tag': Term.objects.get(slug=self.kwargs['term']),
            self.kwargs['taxonomy']: self.kwargs['term'],
        })
        return context

    def get_queryset(self):
        taxonomy = TAXONOMIES.get(self.kwargs['taxonomy'], None)
        if taxonomy:
            tag = get_object_or_404(Term, slug=self.kwargs['term'])
            return Post.objects.term(tag.name, taxonomy=taxonomy).select_related()


class TermArchive(generic.list.ListView):
    pass
