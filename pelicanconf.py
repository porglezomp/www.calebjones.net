#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'C Jones'
SITENAME = 'J Language Comment'
SITESUBTITLE = "C Jones' Blog"
SITEURL = ''

MENUITEMS = [
    ('Blog', '/'),
]

PATH = 'content'

TIMEZONE = 'EST'

DEFAULT_DATE_FORMAT = '%B %d, %Y'
DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_DOMAIN = SITEURL
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

DEFAULT_PAGINATION = 5

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
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
TAG_URL = 'tag/{slug}/'
TAG_SAVE_AS = TAG_URL + 'index.html'

MARKDOWN = {
    'extension_config': {
        'markdown.extensions.fenced_code': {},
        'markdown.extensions.codehilite': {'css_class': 'highlight'},
        'markdown.extensions.headerid': {'level': 3},
        'markdown.extensions.extra': {},
        'markdown.extensions.meta': {},
    },
    'extensions': [
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.headerid',
        'markdown.extensions.extra',
        'markdown.extensions.meta',
    ],
    'output_format': 'html5',
}
