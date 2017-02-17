import collections
import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


STATUS_CHOICES = (
    ('closed', 'closed'),
    ('open', 'open'),
)

POST_STATUS_CHOICES = (
    ('draft', 'draft'),
    ('inherit', 'inherit'),
    ('private', 'private'),
    ('publish', 'publish'),
)

POST_TYPE_CHOICES = (
    ('attachment', 'attachment'),
    ('page', 'page'),
    ('post', 'post'),
    ('revision', 'revision'),
)

USER_STATUS_CHOICES = (
    (0, "active"),
)

READ_ONLY = getattr(settings, "WP_READ_ONLY", True)
TABLE_PREFIX = getattr(settings, "WP_TABLE_PREFIX", "wp")


#
# Exceptions
#

class WordPressException(Exception):
    """
    Exception that is thrown when attempting to save a read-only object.
    """
    pass


#
# Base managers
#

class WordPressManager(models.Manager):
    """
    Base manager for wordpress queries.
    """
    pass


#
# Base models
#

class WordPressModel(models.Model):
    """
    Base model for all WordPress objects.

    Overrides save and delete methods to enforce read-only setting.
    Overrides self.objects to enforce WP_DATABASE setting.
    """

    objects = WordPressManager()

    class Meta:
        abstract = True
        managed = False

    def _get_object(self, model, obj_id):
        try:
            return model.objects.get(pk=obj_id)
        except model.DoesNotExist:
            pass

    def save(self, override=False, **kwargs):
        if READ_ONLY and not override:
            raise WordPressException("object is read-only")
        super(WordPressModel, self).save(**kwargs)

    def delete(self, override=False):
        if READ_ONLY and not override:
            raise WordPressException("object is read-only")
        super(WordPressModel, self).delete()


#
# WordPress models
#

class OptionManager(WordPressManager):
    def get_value(self, name):
        try:
            o = self.get(name=name)
            return o.value
        except ObjectDoesNotExist:
            pass


class Option(WordPressModel):

    objects = OptionManager()

    id = models.IntegerField(db_column='option_id', primary_key=True)
    name = models.CharField(max_length=64, db_column='option_name')
    value = models.TextField(db_column='option_value')
    autoload = models.CharField(max_length=20)

    class Meta:
        db_table = '%s_options' % TABLE_PREFIX
        ordering = ["name"]
        managed = False

    def __unicode__(self):
        return u"%s: %s" % (self.name, self.value)


class User(WordPressModel):
    """
    User object. Referenced by Posts, Comments, and Links
    """

    login = models.CharField(max_length=60, db_column='user_login')
    password = models.CharField(max_length=64, db_column='user_pass')
    username = models.CharField(max_length=255, db_column='user_nicename')
    email = models.CharField(max_length=100, db_column='user_email')
    url = models.URLField(max_length=100, db_column='user_url', blank=True)
    date_registered = models.DateTimeField(auto_now_add=True, db_column='user_registered')
    activation_key = models.CharField(max_length=60, db_column='user_activation_key')
    status = models.IntegerField(default=0, choices=USER_STATUS_CHOICES, db_column='user_status')
    display_name = models.CharField(max_length=255, db_column='display_name')

    class Meta:
        db_table = '%s_users' % TABLE_PREFIX
        ordering = ["display_name"]
        managed = False

    def __unicode__(self):
        return self.display_name


class UserMeta(WordPressModel):
    """
    Meta information about a user.
    """

    id = models.IntegerField(db_column='umeta_id', primary_key=True)
    user = models.ForeignKey(User, related_name="meta", db_column='user_id')
    key = models.CharField(max_length=255, db_column='meta_key')
    value = models.TextField(db_column='meta_value')

    class Meta:
        db_table = '%s_usermeta' % TABLE_PREFIX
        managed = False

    def __unicode__(self):
        return u"%s: %s" % (self.key, self.value)


class Link(WordPressModel):
    """
    An external link.
    """

    id = models.IntegerField(db_column='link_id', primary_key=True)
    url = models.URLField(max_length=255, db_column='link_url')
    name = models.CharField(max_length=255, db_column='link_name')
    image = models.CharField(max_length=255, db_column='link_image')
    target = models.CharField(max_length=25, db_column='link_target')
#    category_id = models.IntegerField(default=0, db_column='link_category')
    description = models.CharField(max_length=255, db_column='link_description')
    visible = models.CharField(max_length=20, db_column='link_visible')
    owner = models.ForeignKey(User, related_name='links', db_column='link_owner')
    rating = models.IntegerField(default=0, db_column='link_rating')
    updated = models.DateTimeField(blank=True, null=True, db_column='link_updated')
    rel = models.CharField(max_length=255, db_column='link_rel')
    notes = models.TextField(db_column='link_notes')
    rss = models.CharField(max_length=255, db_column='link_rss')

    class Meta:
        db_table = '%s_links' % TABLE_PREFIX
        managed = False

    def __unicode__(self):
        return u"%s %s" % (self.name, self.url)

    def is_visible(self):
        return self.visible == 'Y'


class PostManager(WordPressManager):
    """
    Provides convenience methods for filtering posts by status.
    """

    def _by_status(self, status, post_type='post'):
        return self.filter(status=status, post_type=post_type)\
            .select_related().prefetch_related('meta')

    def drafts(self, post_type='post'):
        return self._by_status('draft', post_type)

    def private(self, post_type='post'):
        return self._by_status('private', post_type)

    def published(self, post_type='post'):
        return self._by_status('publish', post_type)

    def term(self, terms, taxonomy='post_tag'):
        """
        @arg terms Can either be a string (name of the term) or an list of term names.
        """

        terms = terms if isinstance(terms, (list, tuple)) else [terms]

        try:
            tx = Taxonomy.objects.filter(name=taxonomy, term__slug__in=terms)
            post_ids = TermTaxonomyRelationship.objects.filter(term_taxonomy__in=tx).values_list('object_id', flat=True)

            return self.published().filter(pk__in=post_ids)
        except Taxonomy.DoesNotExist:
            return self.none()

    def from_path(self, path):

        (ymd, slug) = path.strip('/').rsplit('/', 1)

        start_date = datetime.datetime.strptime(ymd, "%Y/%m/%d")
        end_date = start_date + datetime.timedelta(days=1) - datetime.timedelta(minutes=1)

        params = {
            'post_date__range': (start_date, end_date),
            'slug': slug,
        }

        try:
            return self.published().get(**params)
        except ObjectDoesNotExist:
            pass  # fall through to return None


class TermTaxonomyRelationship(WordPressModel):

    object = models.ForeignKey('Post')
    term_taxonomy = models.ForeignKey('Taxonomy', related_name='relationships', db_column='term_taxonomy_id')
    order = models.IntegerField(db_column='term_order')

    class Meta:
        db_table = '%s_term_relationships' % TABLE_PREFIX
        ordering = ['order']
        managed = False


class Post(WordPressModel):
    """
    The mother lode.
    The WordPress post.
    """

    objects = PostManager()

    id = models.AutoField(primary_key=True, db_column='ID')

    # post data
    guid = models.CharField(max_length=255)
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES)
    status = models.CharField(max_length=20, db_column='post_status', choices=POST_STATUS_CHOICES)
    title = models.TextField(db_column='post_title')
    slug = models.SlugField(max_length=200, db_column="post_name")
    author = models.ForeignKey(User, related_name='posts', db_column='post_author')
    excerpt = models.TextField(db_column='post_excerpt')
    content = models.TextField(db_column='post_content')
    content_filtered = models.TextField(db_column='post_content_filtered')
    post_date = models.DateTimeField(db_column='post_date')
    modified = models.DateTimeField(db_column='post_modified')

    # comment stuff
    comment_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    comment_count = models.IntegerField(default=0)

    # ping stuff
    ping_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    to_ping = models.TextField()
    pinged = models.TextField()

    # statuses
    password = models.CharField(max_length=20, db_column="post_password")
#    category_id = models.IntegerField(db_column='post_category')

    # other various lame fields
    parent_id = models.IntegerField(default=0, db_column="post_parent")
    # parent = models.ForeignKey('self', related_name="children", db_column="post_parent", blank=True, null=True)
    menu_order = models.IntegerField(default=0)
    mime_type = models.CharField(max_length=100, db_column='post_mime_type')

    terms = models.ManyToManyField('Taxonomy', through='TermTaxonomyRelationship', blank=True)

    term_cache = None
    child_cache = None

    class Meta:
        db_table = '%s_posts' % TABLE_PREFIX
        get_latest_by = 'post_date'
        ordering = ["-post_date"]
        managed = False

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        if self.parent_id is None:
            self.parent_id = 0
        super(Post, self).save(**kwargs)
        self.child_cache = None
        self.term_cache = None

    @models.permalink
    def get_absolute_url(self):
        return ('wp_object_detail', (
            self.post_date.year,
            "%02i" % self.post_date.month,
            "%02i" % self.post_date.day,
            self.slug
        ))

    # cache stuff

    def _get_children(self):
        if self.child_cache is None:
            self.child_cache = list(Post.objects.filter(parent_id=self.pk))
        return self.child_cache

    def _get_terms(self, taxonomy):

        if not self.term_cache:

            self.term_cache = collections.defaultdict(list)

            qs = Taxonomy.objects.filter(relationships__object_id=self.id).select_related()
            qs = qs.order_by('relationships__order', 'term__name')

            term_ids = [tax.term_id for tax in qs]

            terms = {}
            for term in Term.objects.filter(id__in=term_ids):
                terms[term.id] = term

            for tax in qs:
                if tax.term_id in terms:
                    self.term_cache[tax.name].append(terms[tax.term_id])

        return self.term_cache.get(taxonomy)

    # properties

    @property
    def children(self):
        return self._get_children()

    @property
    def parent(self):
        if self.parent_id:
            return Post.objects.get(pk=self.parent_id)

    @parent.setter
    def parent(self, post):
        if post.pk is None:
            raise ValueError('parent post must have an ID')
        self.parent_id = post.pk

    # related objects

    def categories(self):
        return self._get_terms("category")

    def attachments(self):
        for post in self._get_children():
            if post.post_type == 'attachment':
                yield {
                    'id': post.id,
                    'slug': post.slug,
                    'timestamp': post.post_date,
                    'description': post.content,
                    'title': post.title,
                    'guid': post.guid,
                    'mimetype': post.mime_type,
                }

    def tags(self):
        return self._get_terms("post_tag")


class PostMeta(WordPressModel):
    """
    Post meta data.
    """

    id = models.IntegerField(db_column='meta_id', primary_key=True)
    post = models.ForeignKey(Post, related_name='meta', db_column='post_id')
    key = models.CharField(max_length=255, db_column='meta_key')
    value = models.TextField(db_column='meta_value')

    class Meta:
        db_table = '%s_postmeta' % TABLE_PREFIX
        managed = False

    def __unicode__(self):
        return u"%s: %s" % (self.key, self.value)


class Comment(WordPressModel):
    """
    Comments to Posts.
    """

    id = models.IntegerField(db_column='comment_id', primary_key=True)
    post = models.ForeignKey(Post, related_name="comments", db_column="comment_post_id")
    user_id = models.IntegerField(db_column='user_id', default=0)
    #user = models.ForeignKey(User, related_name="comments", blank=True, null=True, default=0 )
    parent_id = models.IntegerField(default=0, db_column='comment_parent')

    # author fields
    author_name = models.CharField(max_length=255, db_column='comment_author')
    author_email = models.EmailField(max_length=100, db_column='comment_author_email')
    author_url = models.URLField(blank=True, db_column='comment_author_url')
    author_ip = models.GenericIPAddressField(db_column='comment_author_ip')

    # comment data
    post_date = models.DateTimeField(db_column='comment_date_gmt')
    content = models.TextField(db_column='comment_content')
    karma = models.IntegerField(default=0, db_column='comment_karma')
    approved = models.CharField(max_length=20, db_column='comment_approved')

    # other stuff
    agent = models.CharField(max_length=255, db_column='comment_agent')
    comment_type = models.CharField(max_length=20)

    class Meta:
        db_table = '%s_comments' % TABLE_PREFIX
        ordering = ['-post_date']
        managed = False

    def __unicode__(self):
        return u"%s on %s" % (self.author_name, self.post.title)

    def get_absolute_url(self):
        return "%s#comment-%i" % (self.post.get_absolute_url(), self.pk)

    def parent(self):
        return self._get_object(Comment, self.parent_id)

    """
    def user(self):
        return self._get_object(User, self.user_id)
    """

    def is_approved(self):
        return self.approved == '1'

    def is_spam(self):
        return self.approved == 'spam'


class Term(WordPressModel):

    id = models.IntegerField(db_column='term_id', primary_key=True)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200)
    group = models.IntegerField(default=0, db_column='term_group')

    class Meta:
        db_table = '%s_terms' % TABLE_PREFIX
        ordering = ['name']
        managed = False

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('wp_archive_term', (self.slug, ))


class Taxonomy(WordPressModel):

    id = models.IntegerField(db_column='term_taxonomy_id', primary_key=True)
    term = models.ForeignKey(Term, related_name='taxonomies', blank=True, null=True)
    #term_id = models.IntegerField()
    name = models.CharField(max_length=32, db_column='taxonomy')
    description = models.TextField()
    parent_id = models.IntegerField(default=0, db_column='parent')
    count = models.IntegerField(default=0)

    class Meta:
        db_table = '%s_term_taxonomy' % TABLE_PREFIX
        ordering = ['name']
        managed = False

    def __unicode__(self):
        try:
            term = self.term
        except Term.DoesNotExist:
            term = ''
        return u"%s: %s" % (self.name, term)

    def parent(self):
        return self._get_object(Taxonomy, self.parent_id)

    #def term(self):
    #    return self._get_object(Term, self.term_id)
