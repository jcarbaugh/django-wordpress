# Changelog for django-wordpress

## 0.5

* Django 1.5 support
* fixed incorrect lookups for term views
* added Post.objects.from_path(path) method to load post from WordPress-style URL path

## 0.4

* add class-based views
* deprecate method-based views

## 0.3

* fix multi-database support

## 0.2

* disabled support for Link.category_id and Post.category_id (WordPress 3.x)
* added the *WP_DATABASE* setting to specify which database the wordpress content is coming from
* added mapping for TermTaxonomyRelationship so there is no more hand-crafted SQL being run
* PostManager.term() now supports multiple terms
* added Term.get_absolute_url()
* ensured that WordPress tables are not created or deleted by Django by marking them as unmanaged

Thanks to [twig](https://github.com/twig) for this release!

## 0.1

*   initial release
