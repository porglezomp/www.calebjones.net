#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Caleb Jones'
SITENAME = 'Emacs and Chill'
SITESUBTITLE = "Caleb Jones' Blog"
SITEURL = ''

MENUITEMS = [
    ('Blog', '/'),
]

PATH = 'content'

TIMEZONE = 'EST'

DEFAULT_DATE_FORMAT = '%B %d, %Y'
DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
)

# Social widget
SOCIAL = (
    ('GitHub', 'https://github.com/porglezomp'),
    ('Twitter', 'https://twitter.com/porglezomp'),
)

DEFAULT_PAGINATION = 4

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
THEME = 'theme'

# Disable author pages, since I'm the only one writing content
AUTHOR_URL = ''

# Improve URLS
PAGINATION_PATTERNS = (
    (1, '{base_name}/', '{base_name}/index.html'),
    (2, '{base_name}/page/{number}/', '{base_name}/page/{number}/index.html'),
)

ARTICLE_URL = 'posts/{date:%Y}/{date:%m}/{slug}/'
ARTICLE_SAVE_AS = ARTICLE_URL + 'index.html'
DRAFT_URL = 'drafts/{slug}/'
DRAFT_SAVE_AS = DRAFT_URL + 'index.html'
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = PAGE_URL + 'index.html'
TAG_URL =  'tag/{slug}/'
TAG_SAVE_AS = TAG_URL + 'index.html'
