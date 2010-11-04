from django import template
from django.template import Context
from wordpress.models import Post
import re

register = template.Library()

class PostsContextNode(template.Node):

    def __init__(self, queryset, var_name):
        self.queryset = queryset
        self.var_name = var_name

    def render(self, context):
        context[self.var_name] = self.queryset
        return ''

class PostsTemplateNode(template.Node):
    
    def __init__(self, queryset, nodelist):
        self.queryset = queryset
        self.nodelist = nodelist
        
    def render(self, context):
        content = ''
        for post in self.queryset:
            content += self.nodelist.render(Context({'post': post})) + '\n'
        return content

def _posts(parser, token, queryset):

    m = re.search(r'(?P<tag>\w+)(?: (?P<count>\d{1,4}))?(?: as (?P<var_name>\w+))?', token.contents)
    args = m.groupdict()
    
    if args['count']:
        try:
            queryset = queryset[:int(args['count'])]
        except ValueError:
            raise template.TemplateSyntaxError, "count argument must be an integer"
    
    if args['var_name']:
        return PostsContextNode(queryset, args['var_name'])
        
    else:
        nodelist = parser.parse(('end%s' % args['tag'],))
        parser.delete_first_token()
        return PostsTemplateNode(queryset, nodelist)


@register.tag(name="recentposts")
def do_recent_posts(parser, token):
    qs = Post.objects.published()
    return _posts(parser, token, qs)


# popular tags
"""
SELECT COUNT(1) as cnt, t.name, t.slug
FROM sf_terms t
JOIN sf_term_taxonomy tt ON t.term_id = tt.term_id
JOIN sf_term_relationships tr ON tt.term_taxonomy_id = tr.term_taxonomy_id
JOIN sf_posts p ON tr.object_id = p.id
WHERE p.post_status = 'publish'
    AND p.post_type = 'post'
    AND t.slug <> 'uncategorized'
GROUP BY t.name, t.slug
ORDER BY cnt DESC
LIMIT 10
"""