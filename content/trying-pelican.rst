Trying Pelican
##############
Off-the-Shelf is Good
=====================
:date: 2016-02-04
:tags: meta
:slug: trying-pelican
:author: C Jones
:summary: I restarted my website using Pelican and ReST!
:status: published

I wrote my own Markdown parser because I wanted the option to add features, and to generate more semantic HTML than I was used to with other static site/blogging platforms.
That turned out to be a maintainability problem, and I never got some of the more tricky features like lists (and especially nested lists) working propertly.
Instead, I've decided to use a standard platform, Pelican_, to write my blog and build my site.
I chose Pelican because, while Ruby is nice, I still prefer Python and use it far more frequently.
In addition, Pelican uses reStructuredText_, which is extensible, so if I want to add more features to my documents, I can.
Even by default, reStructuredText has more features than Markdown does [#]_.

.. _Pelican: http://blog.getpelican.com/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. [#] See? It has footnotes!
