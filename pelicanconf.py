#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'janssen'
SITENAME = u'blog.aurka.com'
SITEURL = 'localhost:8000'

THEME = 'themes/html5-dopetrope'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'de'
DEFAULT_DATE_FORMAT = ('%d.%m.%Y')

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (('Pelican', 'http://getpelican.com/'),
          ('Python.org', 'http://python.org/'),
          ('Jinja2', 'http://jinja.pocoo.org/'),
          ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 5

STATIC_PATHS = ["pictures", "krimskrams", ]

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
