#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'Caleb Jones'
SITENAME = u'Emacs and Chill'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'EST'

DEFAULT_DATE_FORMAT = '%B %d, %Y'
DEFAULT_LANG = u'en'
DEFAULT_METADATA = {
    'status': 'draft',
}

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = ()

# Social widget
SOCIAL = (('GitHub', 'https://github.com/porglezomp'),
          ('Twitter', 'https://twitter.com/porglezomp'),
)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
THEME = 'theme'
