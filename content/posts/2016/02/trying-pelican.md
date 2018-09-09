+++
title = "Trying Pelican"
date = 2016-02-04
description = "I restarted my website using Pelican and ReST!"
slug = "trying-pelican"
[extra]
tags = ["meta"]
subtitle = "Off-the-Shelf is Good"
+++

I wrote my own Markdown parser because I wanted the option to add features, and to generate more semantic HTML than I was used to with other static site/blogging platforms.
That turned out to be a maintainability problem, and I never got some of the more tricky features like lists (and especially nested lists) working propertly.
Instead, I've decided to use a standard platform, [Pelican][], to write my blog and build my site.
I chose Pelican because, while Ruby is nice, I still prefer Python and use it far more frequently.
In addition, Pelican uses [reStructuredText][], which is extensible, so if I want to add more features to my documents, I can.
Even by default, reStructuredText has more features than Markdown does.

**Note:** This is now running on [Gutenberg][], which only supports Markdown :(, but Pelican eventually became an upgrade mess.

[Pelican]: http://blog.getpelican.com/
[reStructuredText]: http://docutils.sourceforge.net/rst.html
[Gutenberg]: https://www.getgutenberg.io
