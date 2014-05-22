#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'janssen'
SITENAME = u'aurka.com'
SITESUBTITLE = u'under heavy development'
SITEURL = 'http://aurka.com'

THEME = 'themes/aurka_1'

MENUITEMS = (('Home', 'http://aurka.com'),('Bilder / Mediagoblin', 'http://mediagoblin.aurka.com/mediagoblin/mg.fcgi/u/janssen/'),('Fotografie', 'http://aurka.com/pages/fotografie.html'),('Kategorien', 'http://aurka.com/categories.html'),('About', 'http://aurka.com/pages/about.html'),('Links', 'http://aurka.com/pages/links.html'),)

TIMEZONE = 'Europe/Paris'
DEFAULT_DATE_FORMAT = ('%d.%m.%Y')


DEFAULT_LANG = u'de'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/all.atom.xml' 

FEED_ALL_RSS = 'feeds/all.rss.xml'

# Blogroll
#LINKS =  (('My Photos on 500px', 'http://500px.com/0xTry'),
#          ('My Twitter Accoutn', 'https://twitter.com/0xTry'),)

# Social widget
#SOCIAL = (('Twitter', 'https://twitter.com/0xTry'),
#          ('500px', 'http://500px.com/0xTry'),)

DEFAULT_PAGINATION = 7

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True


DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False

STATIC_PATHS = ["pictures", "krimskrams", ]


#Piwik

PIWIK_URL = 'piwik.aurka.com'
PIWIK_SITE_ID = 2
