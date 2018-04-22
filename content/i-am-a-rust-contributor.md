title: I'm a Rust Contributor
date: 2016-09-20
tags: rust
slug: i-am-a-rust-contributor
author: C Jones
summary: I got a PR merged into Rust, wow, that's pretty cool!

A month or two ago I was on the #rust IRC when someone discovered that `pow()` didn't act quite right for unsigned numbers.
This was a bug that was isolated to a single function, so it seemed like something that I could handle.
The issue got posted, I claimed it and debugged it, and actually managed to fix it!
It took a little while, but very early this morning PR #34942 [*Fix overflow checking in unsigned pow()*][issue34942] was merged.
Now I'm a contributor to Rust!

[issue34942]: https://github.com/rust-lang/rust/pull/34942#event-795131414

Try to find a small thing that you can fix in something that you use.
Somewhere in there is the right issue that you can fix.
It's a great experience.
(I really look forward to the release notes for 1.12...)

**Update:**
It turns out my fix made it into the 1.13 release, and my name is in the [contributors section in the release notes][contributors].

[contributors]: https://blog.rust-lang.org/2016/11/10/Rust-1.13.html#contributors-to-1130
