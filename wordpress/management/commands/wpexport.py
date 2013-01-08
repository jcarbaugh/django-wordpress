import sys

from django.core.management.base import NoArgsCommand, CommandError
from wordpress.models import Post


class Command(NoArgsCommand):

    def handle_noargs(self, **options):

        posts = Post.objects.published()
