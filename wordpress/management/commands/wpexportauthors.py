import csv
import sys

from django.core.management.base import NoArgsCommand
from wordpress.models import User

HEADERS = ("id", "username", "display_name", "email")


class Command(NoArgsCommand):

    def handle_noargs(self, **options):

        writer = csv.writer(sys.stdout)
        writer.writerow(HEADERS)

        for author in User.objects.all():
            row = (
                author.pk,
                author.login,
                author.display_name,
                author.email,
            )
            writer.writerow(row)
