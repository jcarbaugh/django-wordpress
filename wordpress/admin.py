from django.contrib import admin
from wordpress.models import Option, Comment, Link, Post, PostMeta, Taxonomy, Term, User, UserMeta

class OptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','post','author_name','post_date')
    list_filter = ('comment_type','approved')
    search_fields = ('author_name','author_email','post__title')

class LinkAdmin(admin.ModelAdmin):
    list_display = ('id','name','url','description')
    list_filter = ('visible',)
    search_fields = ('name','url','description')

class PostMetaInline(admin.TabularInline):
    model = PostMeta
    
class PostAdmin(admin.ModelAdmin):
    inlines = (PostMetaInline,)
    list_display = ('id','title','author','post_date')
    list_filter = ('status','post_type','comment_status','ping_status','author')
    search_fields = ('title',)
    
class UserMetaInline(admin.TabularInline):
    model = UserMeta
    
class UserAdmin(admin.ModelAdmin):
    inlines = (UserMetaInline,)
    list_display = ('id','display_name','email','status')
    list_filter = ('status',)
    search_fields = ('login','username','display_name','email')

class TaxonomyAdmin(admin.ModelAdmin):
    list_display = ('id','name','term')
    list_filter = ('name',)
    
class TermAdmin(admin.ModelAdmin):
    list_display = ('id','name')
    search_fields = ('name',)

admin.site.register(Option, OptionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Taxonomy, TaxonomyAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(User, UserAdmin)