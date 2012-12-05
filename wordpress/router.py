# -*- coding: utf-8 -*-

from django.conf import settings

DATABASE = getattr(settings, "WP_DATABASE", "default")


class WordpressRouter(object):
    """
    Overrides default wordpress database to WP_DATABASE setting.
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'wordpress':
            return DATABASE
        return None

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)
