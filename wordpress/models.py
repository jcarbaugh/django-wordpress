from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import connections, models
from django.db.models import signals
from django.http import HttpResponseRedirect
import re

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
    ('attachment','attachment'),
    ('page','page'),
    ('post','post'),
    ('revision','revision'),
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
# Base models
#

class WordPressModel(models.Model):
    """
    Base model for all WordPress objects.
    Overrides save and delete methods to enforce read-only setting.
    """
    class Meta:
        abstract = True

    def _get_object(self, model, obj_id):
        try:
            return model.objects.get(pk=obj_id)
        except model.DoesNotExist:
            pass
        
    def save(self, override=False):
        if READ_ONLY and not override:
            raise WordPressException, "object is read-only"
        super(WordPressModel, self).save()
        
    def delete(self, override=False):
        if READ_ONLY and not override:
            raise WordPressException, "object is read-only"
        super(WordPressModel, self).delete()

#
# WordPress models
#

class User(WordPressModel):
    """
    User object. Referenced by Posts, Comments, and Links
    """
    login = models.CharField(max_length=60, db_column='user_login')
    password = models.CharField(max_length=64, db_column='user_pass')
    username = models.CharField(max_length=255, db_column='user_nicename')
    email = models.CharField(max_length=100, db_column='user_email')
    url = models.URLField(max_length=100, db_column='user_url', verify_exists=False)
    date_registered = models.DateTimeField(auto_now_add=True, db_column='user_registered')
    activation_key = models.CharField(max_length=60, db_column='user_activation_key')
    status = models.IntegerField(default=0, choices=USER_STATUS_CHOICES, db_column='user_status')
    display_name = models.CharField(max_length=255, db_column='display_name')

    class Meta:
        db_table = '%s_users' % TABLE_PREFIX
    	ordering = ["display_name"]
    
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
    
    def __unicode__(self):
        return u"%s: %s" % (self.key, self.value)

class Link(WordPressModel):
    """
    An external link.
    """
    id = models.IntegerField(db_column='link_id', primary_key=True)
    url = models.URLField(max_length=255, verify_exists=False, db_column='link_url')
    name = models.CharField(max_length=255, db_column='link_name')
    image = models.CharField(max_length=255, db_column='link_image')
    target = models.CharField(max_length=25, db_column='link_target')
    category_id = models.IntegerField(default=0, db_column='link_category')
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

    def __unicode__(self):
        return u"%s %s" % (self.name, self.url)
    
    def is_visible(self):
        return self.visible == 'Y'
    
class PostManager(models.Manager):
    """
    Provides convenience methods for filtering posts by status.
    """
    
    def _by_status(self, status, post_type='post'):
        return Post.objects.filter(status=status, post_type=post_type)
        
    def drafts(self, post_type='post'):
        return self._by_status('draft', post_type)
        
    def private(self, post_type='post'):
        return self._by_status('private', post_type)
        
    def published(self, post_type='post'):
        return self._by_status('publish', post_type)
        
    def term(self, term, taxonomy='post_tag'):
        term = term.replace('-', ' ')
        tx = Taxonomy.objects.get(name=taxonomy, term__name=term)
        table = '%s_term_relationships' % TABLE_PREFIX
        sql = """SELECT object_id FROM """ + table + """ WHERE term_taxonomy_id = %s"""
        cursor = connections['wordpress'].cursor()
        cursor.execute(sql, [tx.pk,])
        pids = [row[0] for row in cursor.fetchall()]
        return Post.objects.published().filter(pk__in=pids)
    
class Post(WordPressModel):
    """
    The mother lode.
    The WordPress post.
    """
    
    objects = PostManager()
    
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
    post_date = models.DateTimeField(db_column='post_date_gmt')
    modified = models.DateTimeField(db_column='post_modified_gmt')
    
    # comment stuff
    comment_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    comment_count = models.IntegerField(default=0)
    
    # ping stuff
    ping_status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    to_ping = models.TextField()
    pinged = models.TextField()
    
    # statuses
    password = models.CharField(max_length=20, db_column="post_password")
    category_id = models.IntegerField(db_column='post_category')
    
    # other various lame fields
    parent = models.ForeignKey('self', related_name="children", db_column="post_parent", blank=True, null=True)
    menu_order = models.IntegerField(default=0)
    mime_type = models.CharField(max_length=100, db_column='post_mime_type')
    
    category_cache = None
    tag_cache = None
	
    class Meta:
    	db_table = '%s_posts' % TABLE_PREFIX
    	ordering = ["-post_date"]
    	
    def __unicode__(self):
        return self.title
        
    def categories(self):
        if not self.category_cache:
            taxonomy = "category"
            self.category_cache = self._get_terms(taxonomy)
        return self.category_cache
        
    def get_absolute_url(self):
        year = self.post_date.year
        month = self.post_date.month
        day = self.post_date.day
        slug = self.slug
        return reverse('wp_object_detail', args=(year, month, day, slug))
        
    """   
    @models.permalink
    def get_absolute_url(self):
        params = {
            "year": self.post_date.year,
            "month": self.post_date.month,
            "day": self.post_date.day,
            "slug": self.slug,
        }
        return ('wp_object_detail', (), params)
    """
    
    """
    def parent(self):
        return self._get_object(Post, self.parent_id)
    """ 
     
    def tags(self):
        print self.get_absolute_url()
        if not self.tag_cache:
            taxonomy = "post_tag"
            self.tag_cache = self._get_terms(taxonomy)
        return self.tag_cache
        
    def _get_terms(self, taxonomy):
        table = '%s_term_relationships' % TABLE_PREFIX
        sql = """SELECT term_taxonomy_id FROM """ + table + """ WHERE object_id = %s ORDER BY term_order"""
        cursor = connections['wordpress'].cursor()
        cursor.execute(sql, [self.id,])
        ttids = [row[0] for row in cursor.fetchall()]
        return Term.objects.filter(taxonomies__name=taxonomy, taxonomies__pk__in=ttids)
        
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
    author_url = models.URLField(verify_exists=False, db_column='comment_author_url')
    author_ip = models.IPAddressField(db_column='comment_author_ip')
    
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
    slug = models.SlugField(max_length=200)
    group = models.IntegerField(default=0, db_column='term_group')

    class Meta:
        db_table = '%s_terms' % TABLE_PREFIX
        ordering = ['name',]

    def __unicode__(self):
        return self.name

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
        ordering = ['name',]

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