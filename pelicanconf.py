#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'janssen'
SITENAME = u'blog.aurka.com'
#SITESUBTITLE = u''
SITEURL = 'https://blog.aurka.com'

THEME = 'themes/html5-dopetrope'

#MENUITEMS = (('Home', 'http://aurka.com'),('Bilder / Mediagoblin', 'http://mediagoblin.aurka.com/mediagoblin/mg.fcgi/u/janssen/'),('Fotografie', 'http://aurka.com/pages/fotografie.html'),('Tech-Posts', 'http://aurka.com/category/techx.html'),('About', 'http://aurka.com/pages/about.html'),('Links', 'http://aurka.com/pages/links.html'),)

TIMEZONE = 'Europe/Paris'
DEFAULT_DATE_FORMAT = ('%d.%m.%Y')

# Customizing
ABOUT_LINK = 'https://blog.aurka.com/pages/about.html'
ABOUT_IMAGE = 'freshpaint.jpg'

# Category
#CATEGORY_URL = 'category/{slug}.html'

DEFAULT_LANG = u'de'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml'

FEED_ALL_RSS = 'feeds/all.rss.xml'

# Blogroll
#LINKS =  (('My Photos on 500px', 'http://500px.com/janaurka'),
#          ('My Twitter Accoutn', 'https://twitter.com/janaurka'),)

# Social widget
#SOCIAL = (('Twitter', 'https://twitter.com/janaurka'),
#          ('500px', 'http://500px.com/janaurka'),)

DEFAULT_PAGINATION = 7

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True


DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False

STATIC_PATHS = ["pictures", "krimskrams", ]

#PLUGINS = [
#    'pelicanfly',
#]

#Piwik

PIWIK_URL = 'piwik.aurka.com'
PIWIK_SITE_ID = 2
