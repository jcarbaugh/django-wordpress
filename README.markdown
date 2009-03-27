# django-wordpress

Models and views for reading a WordPress database. Compatible with WordPress version 2.6.1.

These models are meant to be read-only. Writing is enabled by adding *WP_READ_ONLY = False* to settings.py. None of the WordPress specific logic is included while writing to the database so there is a good chance you will break your WordPress install if you enable writing.

The default table prefix is *wp*. To change the table prefix, add *WP_TABLE_PREFIX = 'yourprefix'* to settings.py.

Default templates are provided only for development purposes! Please override these with customized templates for your application.

django-wordpress is a project of Sunlight Foundation (c) 2009.
Writen by Jeremy Carbaugh <jcarbaugh@sunlightfoundation.com>

All code is under a BSD-style license, see LICENSE for details.

Source: http://github.com/sunlightlabs/django-wordpress/


## Requirements

python >= 2.4

django >= 1.0


## Installation

To install run

    python setup.py install

which will install the application into python's site-packages directory.


## Quick Setup


### settings.py

Add to INSTALLED_APPS:

    'wordpress'


### urls.py

Include the following in urls.py.

    url(r'^path/to/blog/', include('wordpress.urls')),


## Help!

The term/taxonomy support is quite shoddy. Any help in that area would be greatly appreciated.