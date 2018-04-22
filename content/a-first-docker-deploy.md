title: A First Docker Deploy
date: 2016-07-01
tags: docker; rust; nginx
slug: a-first-docker-deploy
author: C Jones
summary: I try to deploy a webservice to AWS using Docker
status: draft

Last time I gushed about Docker's setup experience.
This time I'm going to try to use this newfound power to deploy a Rust app to AWS on Alpine Linux, with HTTPS through Nginx.
I want to use Nginx so that I don't have to worry about HTTPS at the Rust level, since the highest performance Rust framework currently only supports plain HTTP.
Furthermore, if I ever needed to branch out into load balancing or serving static assets, Nginx would be there already.
If you want to follow along, then just `cargo new` and we'll get started!

# A Rusty Container

In [Creating a Basic Webservice in Rust][webservice] they use Docker in order to statically link the executable with musl, not to deploy it.
Here we're going to go a step further and do the entire deployment with Docker.
In order to do this, we'll still want a binary that's statically linked against the musl libc, so that we can run it on Alpine Linux which doesn't package glibc.
It's possible to do this using cross-compiler toolchains with [rustup][], but when I tried to compile for `x86_64-unknown-linux-musl` on my Mac, I got a lot of linker errors.
Instead of trying to fix that, we're going to use the Docker image suggested in that article, [rust-musl-builder][].
For our build process, I create `build.sh` at the root of my crate:

    ::sh
    #!/bin/sh
    docker run --rm -it -v "$(pwd)":/home/rust/src ekidd/rust-musl-builder cargo build --release

We'll run this whenever we want to rebuild our static binary. 

[webservice]: http://hermanradtke.com/2016/05/16/creating-a-basic-webservice-in-rust.html
[rustup]: https://www.rustup.rs/
[rust-musl-builder]: https://github.com/emk/rust-musl-builder

Speaking of that static binary, we need a program to run!
For now, we'll run a tiny demo program that returns a simple JSON response.
Here's the `Cargo.toml` so we can use [the nickel framework][]:

    ::toml
    [package]
    name = "example-webservice"
    version = "0.1.0"
    authors = ["Caleb Jones <self@calebjones.net>"]

    [dependencies]
    nickel = "0.8.1"

[the nickel framework]: http://nickel.rs/ 

And here's the code for the demo webservice in `src/main.rs`:

    ::rust
    #[macro_use] extern crate nickel;

    use nickel::{Nickel, MediaType};

    fn main() {
        let mut server = Nickel::new();

        server.utilize(router! {
            get "/" => |_request, mut response| {
                response.set(MediaType::Json);
                r#"{ "message": "Hello, World!" }"#
            }
            get "/:name" => |request, mut response| {
                response.set(MediaType::Json);
                format!(r#"{{ "message": "Hello, {}!" }}"#,
                        request.param("name").unwrap())
            }
        });

        server.listen("0.0.0.0:8080");
    }

# Composing a Server

Now we want to set up an Nginx reverse proxy.
At first I was confused about how to combine multiple programs into a single `Dockerfile`, since it only executes one `CMD`.
Should I write I script that invokes `nginx` and then my server, and then make that the `CMD`?
Through some investigation, the Docker philosophy became more clear though.
You should put one component in each container, and in this case the Nginx proxy is a separate component from the webservice itself.
Of course, realizing this opened up a whole new series of questions, like how do I sensibly start my two Docker containers together?
