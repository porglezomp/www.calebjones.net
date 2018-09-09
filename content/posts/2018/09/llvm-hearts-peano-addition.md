+++
title = "LLVM 💖s Peano Addition"
date = 2018-09-07
description = "I am surprised to discover that LLVM can optimize the standard peano definition of addition, so I set out to investigate."
slug = "llvm-hearts-peano-addition"
[extra]
tags = ["llvm", "compilers", "optimization"]
+++

This semester I'm taking an advanced compilers class.
We're going to be learning by making changes to LLVM, so for the first assignment I was reading recommended [introduction to LLVM][].
In order to give an example of some LLVM IR, it provides two small C functions implementing addition in different ways, and equivalent IR.

[introduction to LLVM]: http://www.aosabook.org/en/llvm.html

```c
unsigned add1(unsigned a, unsigned b) {
  return a+b;
}

// Perhaps not the most efficient way to add two numbers.
unsigned add2(unsigned a, unsigned b) {
  if (a == 0) return b;
  return add2(a-1, b+1);
}
```

Being something of a mathematician myself, I felt I had to [defend the honor][] of "Peano-likers" from this defamation.
I made that joke tweet and moved on, but after [someone suggested LLVM optimize it][suggestion], I started to think about writing some of those optimization passes as hopefully easy pattern-matching definitions.

[defend the honor]: https://twitter.com/porglezomp/status/1037408309140221952
[suggestion]: https://twitter.com/hyperfekt/status/1037654687024119808

The next day, after compiling LLVM and getting a custom Hello World optimizer pass running, I decided to create some tests, and discovered (much to my surprise) that LLVM already handled Peano-style addition and multiplication perfectly competently!

I had just read John Regehr's [blog post on how LLVM optimizes a function][regehr], so I had an idea for how to investigate this.
If you haven't read that yet, you should go read that first in order to see in some more detail LLVM's optimization passes like the ones I'm going to describe below.

[regehr]: https://blog.regehr.org/archives/1603

<!-- more -->

## How to View the Optimizations

That blog post proceeds by running the LLVM `opt` tool and examining the changes between passes.
You can easily get the LLVM IR corresponding to some C code using `clang`, just run:

```shell
$ clang peano.c -emit-llvm -S -o peano.ll
```

and you'll have a beautiful LLVM IR dump in the textual format.
In order to view the optimizations on that code, you can run:

```shell
$ opt -O3 -print-before-all -print-after-all peano.ll
```

This gives you a huge wall of IR dumps after each optimization pass.
If you want to do a similar investigation yourself, I wrote [a Python script that shows each pass's diff][diff script] and waits for you to continue it.
Make sure you have [`icdiff`][] (a very nice color diff tool) installed in order to use it, or else modify the diff invocation in the script.

[diff script]: https://gist.github.com/porglezomp/f2dc233f971cf3f30d45e0b501ae5ead
[`icdiff`]: https://github.com/jeffkaufman/icdiff

## The Optimizations

As you can see from [John Regehr's blog post][regehr], LLVM's passes sometimes undo and redo lots of work without changing very much when working on a function this simple.
Furthermore, the code emitted by the Clang frontend is a little bit of a mess that needs quite a bit of cleanup before it's decent code, in order to avoid needing to reimplement analyses that LLVM can do perfectly well itself.

In order to make this discussion clearer, I'll use the hand-written IR from the introductory article rather than the IR emitted by clang, and only run through the necessary passes to get the job done, not the whole `-O3` pipeline.
At each step of the optimization, I'll provide the IR, and some roughly corresponding C code.

### The Program

We'll be investigating this recursive definition of addition:

```llvm
define i32 @add(i32 %a, i32 %b) {
entry:
  %tmp1 = icmp eq i32 %a, 0
  br i1 %tmp1, label %done, label %recurse

recurse:
  %tmp2 = sub i32 %a, 1
  %tmp3 = add i32 %b, 1
  %tmp4 = call i32 @add(i32 %tmp2, i32 %tmp3)
  ret i32 %tmp4

done:
  ret i32 %b
}
```

Which corresponds to this C program:

```c
typedef unsigned nat;

nat add(nat a, nat b) {
  if (a == 0) return b;
  return add(a-1, b+1);
}
```


### Tail Call Optimization

The first important optimization here is tail call optimization.
Above we see that we call `@add` into `%tmp4` and then immediately return it without doing anything else in between, which makes this a tail call.
Therefore, in order to avoid the cost of calling functions, the extra stack frames needed, and the expose more opportunities for optimizations, tail call optimization turns our tail recursion into a loop.

```llvm
define i32 @add(i32 %a, i32 %b) {
entry:
  br label %tailrecurse

tailrecurse:
  %a.tr = phi i32 [ %a, %entry ], [ %tmp2, %recurse ]
  %b.tr = phi i32 [ %b, %entry ], [ %tmp3, %recurse ]
  %tmp1 = icmp eq i32 %a.tr, 0
  br i1 %tmp1, label %done, label %recurse

recurse:
  %tmp2 = sub i32 %a.tr, 1
  %tmp3 = add i32 %b.tr, 1
  br label %tailrecurse

done:
  ret i32 %b.tr
}
```

This code approximately corresponds to:

```c
nat add(nat a, nat b) {
  while (a != 0) {
    a -= 1;
    b += 1;
  }
  return b;
}
```

By removing the recursive call, further optimizations become visible.
In particular...

### Induction Variable Simplification

Loop optimizations are a primary focus of compiler optimizations, because many programs spend most of their time in a few loops, making those loops faster is the most fruitful optimization.
"Induction Variable Simplification" is a specific optimization that works on identified "loop induction variables", variables that change by a constant amount each loop iteration, or that are derived from other induction variables.

Here, `a` and `b` are identified as loop induction variables.
Event more critically, `a` is the induction variable that controls the loop condition, so `a` is counting down towards `0`.
Therefore, LLVM can determine that the loop will run exactly `a` times, called the "trip count."

In cases where one of the induction variables is used after the loop and the trip count is statically known, LLVM performs an optimization where it computes the final value of the induction variable outside the loop, which splits the live range of the induction variable, and potentially makes it eligible for dead code elimination (which happens in this case).

```llvm
define i32 @add(i32 %a, i32 %b) {
entry:
  br label %tailrecurse

; Loop:
tailrecurse:
  %a.tr = phi i32 [ %a, %entry ], [ %tmp2, %recurse ]
  %tmp1 = icmp eq i32 %a.tr, 0
  br i1 %tmp1, label %done, label %recurse

recurse:
  %tmp2 = sub i32 %a.tr, 1
  br label %tailrecurse

; Exit blocks
done:
  %0 = add i32 %b, %a
  ret i32 %0
}
```

This IR looks basically like this C:

```c
nat add(nat a, nat b) {
  nat a0 = a;
  while (a0 != 0) {
    a0 -= 1;
  }
  return b + a;
}
```

If you're interested in more details of these loop optimizations, my knowledge here comes from [some very nice lecture notes][] linked from Regehr's blog post, go read that if you want to know more about how you actually detect these cases.

[some very nice lecture notes]: https://www.cs.cmu.edu/~fp/courses/15411-f13/lectures/17-loopopt.pdf

### Delete Dead Loops

This pass is very straightforward.
The loop doesn't do anything anymore, and we know it will terminate, so we can just get rid of it.

```llvm
define i32 @add(i32 %a, i32 %b) {
entry:
  %0 = add i32 %b, %a
  ret i32 %0
}
```

And therefore, our code has been optimized down to:
```c
nat add(nat a, nat b) {
  return b + a;
}
```

Our recursive definition of addition turns out to actually be addition, and LLVM has proved it for us!

## Takeaways

Very general optimizations can combine together to have some very surprising specific results, and optimizing compilers are very clever.

These same optimizations work to optimize Peano multiplication, since the loop induction variables like to work with linear functions, but they don't succeed with saturating subtraction, recursive comparisons, or min/max.
It'll be interesting to see if I can come up with a loop optimization pass that can deal with those more complicated trip counts / induction variables in general at all, or if I'll only succeed at pattern matching these very specific functions.
