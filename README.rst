================
django-wordpress
================

Models and views for reading a WordPress database. Compatible with WordPress version 3.5+.

django-wordpress is a project of `ISL <https://isl.co>`_ and the `Sunlight Foundation <http://sunlightfoundation.com>`_.


--------
Features
--------

Read-only models to protect your content
========================================

This package is **designed to be read-only**. Writing is enabled by adding ``WP_READ_ONLY = False`` to settings.py. None of the WordPress specific logic is included while writing to the database so there is a good chance you will break your WordPress install if you enable writing.

WordPress table prefix
======================

The default table prefix is *wp*. To change the table prefix, add ``WP_TABLE_PREFIX = 'yourprefix'`` to settings.py.

Multiple database support
=========================

Added the ability to specify which database the WordPress content is coming from. Set it using the *WP_DATABASE* setting. Defaults to "default".

Database routers need be set to::

    DATABASE_ROUTERS = ['wordpress.router.WordpressRouter']

Default templates
=================

Default templates are provided only for development purposes so you can see content in your browser! Please override these with customized templates for your application.

Export Management Commands
==========================

* *wpexport* Dump published posts in WXR format.
* *wpexportauthors* Export authors as CSV.

-----------------------------
Working With WordPress Models
-----------------------------

Ten most recent published posts::

    Posts.objects.published()[:10]

Posts tagged *wordpress*::

    Posts.objects.term("wordpress")

Post attachments::

    for attachment in post.attachments():
        pass

Post tags::

    post.tags()


------------
Installation
------------

::

    pip install the-real-django-wordpress

Add to INSTALLED_APPS in settings.py::

    'wordpress'

Include the following in urls.py::

    url(r'^path/to/blog/', include('wordpress.urls')),
