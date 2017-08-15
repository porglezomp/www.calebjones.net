title: You Got Your Race Condition Inside My Package Manager!
date: 2017-08-14
tags: python; PyPI; debugging
slug: package-manager-race-condition
author: Caleb Jones
summary: We solve a fun, surreal debugging mystery involving pip and version compatibility.

# A Case of Broken Builds

The continuous integration servers at my current job are unfortunately stateful.
Every week or so, we run a bunch of configuration processes to reinstall packages to keep the environment clean.
One of these reinstalls `pip` and the Python libraries used by build tools.
This morning, I got a message from one of the build engineers telling me that the Python libraries weren't installing correctly anymore.
(Even though I'm an intern, I'm apparently one of the office Python experts now.)
So, I opened up the build log, and began looking around.

What was failing was pretty clear:

```
Collecting ruamel.yaml
  Using cached ruamel.yaml-0.15.28.tar.gz
Installing collected packages: ruamel.yaml
 ...
 error: Microsoft Visual C++ 9.0 is required
```

but why was this suddenly happening now, without us making any changes to our configuration?
Also, why are we installing ruamel.yaml?
We're not using that!

Long story short, ruamel.yaml was a transitive dependency of dateparser, an excellent library for parsing natural language dates.
It wasn't clear to me why it would be suddenly failing though, so I decided to go investigating further.
Looking at the release notes of dateparser, I saw that they had recently pinned ruamel.yaml to `<0.14`, which we clearly weren't getting.
Previously, the version was un-pinned, so I decided to go look at the release notes for ruamel.yaml, and sure enough, there were releases over the weekend—those must've been what broke it.

We upgraded our dependency on dateparser to 0.6, and tried again... and it still failed while trying to build the newest version of ruamel.yaml.
One period of looking at GitHub blame views, commit histories, and unpacking PyPI tarballs later, I determined that version 0.6 of dateparser released on PyPI doesn't actually have the pin the version of ruamel.yaml, despite what the changelog claims.
(I opened [dateparser issue #342][] for this.)

Since the version wasn't pinned, we just asked pip to first install an older version of ruamel.yaml, to hopefully get priority when dateparser tried to install it.
So, we put `ruamel.yaml==0.13.14` in our package list, and then tried again.
Finally, everything worked perfectly.

Case closed.

---

# This Fix is a Mystery

But wait, what's this?
Looking closer at the successful build logs, we can see that both `ruamel.yaml-0.13.14` and `ruamel.yaml-0.15.29` are installing without complaint.
What's stopped the error?
Well, if you'll look at the version number up at the top, we were installing `ruamel.yaml-0.15.28` before—just one hour previously, while I was on my lunch break, an update to ruamel.yaml had been released.
Looking back at previous versions on PyPI, I finally figured out what had gone wrong.
If you look at the downloads on the PyPI page for [ruamel.yaml version 0.15.28][0.15.28], you'll see that there are no Windows wheels.
(Wheels are the format that Python uses to distribute compiled C extensions and pre-packed libraries.)
However, if you go to the page for [version 0.15.29][0.15.29], then you'll see that Windows wheels are finally present.
So, I guess until dateparser fixes their version pinning, we'll just have to hope that ruamel.yaml stays packaged correctly.

Case closed.

---

# We Get Very Unlucky

Oops, nope it's not.
Later in the afternoon, I got another message that some of the builds had failed.
Looking at the first build that started failing, again we see that...

```
Collecting ruamel.yaml
  Using cached ruamel.yaml-0.15.30.tar.gz
Installing collected packages: ruamel.yaml
 ...
 error: Microsoft Visual C++ 9.0 is required
```

okay, this project releases *fast*, this is the fourth release in 2 days.
In any case, the last few builds succeeded with `0.15.30`, so what happened?
Well, I don't know for sure, but I have a pretty good guess.
I suspect that the release process for ruamel.yaml isn't atomic, and that they upload their source releases first, and the wheels come a bit later.
We were unlucky enough to start a build during that first upload, where only the source package was available, and no Windows wheels.
But, the few builds that got held up and started 4 minutes after the others took long enough that the wheels were available, and so they installed without any fuss.

This was an exceptionally unlucky 
But, I've got a very good story now—and also a much greater appreciation for various package manager `.lock` files.

[dateparser issue #342]: https://github.com/scrapinghub/dateparser/issues/342
[0.15.28]: https://pypi.python.org/pypi/ruamel.yaml/0.15.28
[0.15.29]: https://pypi.python.org/pypi/ruamel.yaml/0.15.29
