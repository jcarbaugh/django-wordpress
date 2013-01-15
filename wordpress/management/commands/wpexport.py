import sys

from django.core.management.base import NoArgsCommand
from django.template.loader import render_to_string

from wordpress.models import Post, Author
import wordpress


class Command(NoArgsCommand):

    def handle_noargs(self, **options):

        context = {
            'authors': Author.objects.all(),
            'posts': Post.objects.published(),
            'generator': 'http://github.com/sunlightlabs/django-wordpress#%s' % wordpress.__version__,
        }

        sys.stdout.write(render_to_string("wordpress/wxr.xml", context))
