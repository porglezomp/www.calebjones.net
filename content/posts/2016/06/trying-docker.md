+++
title = "Trying Docker"
date = 2016-06-29
description = "I want to deploy web apps, so I decided to install Docker."
slug = "trying-docker"
[author]
tags = ["docker"]
+++

I only vaguely know what Docker is, but I know the pain of manually installing the requirements of a piece of software.
A few days ago I read [Creating a Basic Webservice in Rust][] and it inspired me to go back and look at Docker again.
I have several ideas for small webservices knocking around in my head right now, so I figured "why not try to deploy them right?"

[Creating a Basic Webservice in Rust]: http://hermanradtke.com/2016/05/16/creating-a-basic-webservice-in-rust.html

The first thing I did was go to [the Docker site][].
The newest version on OS X is a fancy application with some GUI components and a nice menu whale icon.
Installing and getting started is a breeze as well, the [getting started on Mac docs][] show every step with pictures, and event walk you through some examples.

[the Docker site]: https://www.docker.com/ 
[getting started on Mac docs]: https://docs.docker.com/docker-for-mac/

Trying out some of the examples shows a few cool things right away.
One, trying the nginx example

```
$ docker run -d -p 80:80 --name webserver nginx
Unable to find image 'nginx:latest' locally
latest: Pulling from library/nginx
51f5c6a04d83: Downloading 30.41 MB/51.36 MB
a3ed95caeb02: Download complete 
51d229e136d0: Download complete
bcd41daec8cc: Download complete 
```

you can see that multiple downloads took place concurrently, the largest one is still running.
Once it completes, just going to `localhost` shows that we now have a webserver running beautifully, with essentially no setup.
I also notice that when I was starting the server, I mapped port 80 inside the container to port 80 outside.
Again, coming at this with essentially no experience, I hadn't realized quite how much Docker did for you.

Now that I've made it through the Mac getting started page, I'm going to move on to the [Getting Started With Docker][] page.
It's exceptionally well written and self-explanatory, and the Docker docs (at least all the introductory ones I've looked at so far) are just as helpful.

[Getting Started With Docker]: https://docs.docker.com/engine/getstarted/

```
$ docker run docker/whalesay cowsay $(fortune)
_________________________________________ 
/ I worked in a health food store once. A \
| guy came in and asked me, "If I melt    |
| dry ice, can I take a bath without      |
\ getting wet?" -- Steven Wright          /
----------------------------------------- 
    \
    \
      \     
                    ##        .            
              ## ## ##       ==            
          ## ## ## ##      ===            
      /""""""""""""""""___/ ===        
  ~~~ {~~ ~~~~ ~~~ ~~~~ ~~ ~ /  ===- ~~~   
      \______ o          __/            
        \    \        __/             
          \____\______/   
```

I haven't even *really* used Docker yet, but from a first impression I love the experience.
The docs are great, the interface is great, even just the Whale aesthetic is really cute.
I'm going to go back to experimenting with this and tell you how to deploy a program next time.
