+++
title = "Computing Min"
date = 2018-08-27
description = "I benchmark a few different implementations of min, because that's fun."
slug = "computing-min"
[extra]
tags = ["rust", "benchmarking"]
+++

Inspired by the ["gamedev wishlist for rust"][], I got curious if computing the minimum of a bunch of numbers with `min(min(min(a, b), c), d)` was effective.
My thinking was that this would produce unnecessary dependency chains in the processor, stopping out-of-order executions of independent `min`s.
Also, this was a good excuse to try out [Criterion][], so I set out to measure the impact.

["gamedev wishlist for rust"]: https://users.rust-lang.org/t/my-gamedever-wishlist-for-rust/2859
[Criterion]: https://github.com/japaric/criterion.rs

## Implementation

In my actual benchmark I produced two copies of each of these methods specified here.
One for `std::cmp::min`, and one for `f32` (since it's not `Ord`).
For simplicity, I'll just use the generic one here, they both look pretty much the same.

### Loopy

First, I was curious if a usual `.iter().min()` would perform well.
The theory here is that *ideally*, for a known list length, if the compiler thought it was worthwhile, this would compile to the same code as a straight line of `min`.
So, our first case is this:

```rust
[a, b, c, d, e].iter().min()
```

### Linear Reduction Macro

The second method is a macro that will turn `min!(a, b, c, d, e)` into `min(a, min(b, min(c, min(d, e))))`.
This is a direct recursive macro that that just accumulates the `min` calls.
If you're familiar with Rust macros, nothing *too* scary is going on here.

```rust
#[macro_export]
macro_rules! min {
    ($x:expr $(,)*) => { $x };
    ($x:expr $(, $y:expr)* $(,)*) => { ::std::cmp::min($x, min!($($y),*)) };
}
```

<!-- more -->

### Tree Reduction Macro

This macro is quite hairy.
The goal is to turn something like `min_tree!(a, b, c, d, e)` into `min(min(a, min(c, e)), min(b, d))` in order to allow the processor to simultaneously execute the leaf `min` calls.
Let me walk us through the parts:

First, we have the `()` case.
The `Ord` typeclass doesn't offer us a top element, so we just give an error if there are no arguments.
(The float version returns `f32::INFINITY` in this case.)

Next, we have the base cases.
These look very similar to the cases from the `min!` macro, except that the n-element case calls the `@split` case.
The `@split` cases are dedicated to taking a list of expressions, and partitioning it into two different lists of expressions.
The idea being that if you can split it into two lists, then you can do `min_tree!` to each of those two lists.
The first `@split` case pulls two items off the arguments if they're available, and puts one in each accumulator list.
The second case is if there's only one argument left, and the final case is for when there are no arguments left.
Once the argument list has been split into two parts, we do `min(min_tree!(a...), min_tree!(b...))`, recursively constructing the tree.

```rust
#[macro_export]
macro_rules! min_tree {
    () => { compile_error!("Cannot compute the minimum of 0 elements") };
    ($x:expr) => { $x };
    ($x:expr, $y:expr) => { ::std::cmp::min($x, $y) };
    ($($x:expr),* $(,)*) => { min_tree!(@split []; []; $($x),*) };
    (@split [$($a:expr),*]; [$($b:expr),*]; $x:expr, $y:expr $(, $z:expr)*) => {
        min_tree!(@split [$x $(, $a)*]; [$y $(, $b)*]; $($z),*)
    };
    (@split [$($a:expr),*]; [$($b:expr),*]; $x:expr) => {
        min_tree!(@split [$x $(, $a)*]; [$($b),*];)
    };
    (@split [$($a:expr),*]; [$($b:expr),*];) => {
        ::std::cmp::min(min_tree!($($a),*), min_tree!($($b),*))
    };
}
```

## Results

First of all, I was right, tree reduction is faster, at least for the 10-element `min` I was benchmarking.
This is imagining in the context of graphics applications, so we expect relatively small cases, often of a known size (like finding the minimum among 8 neighbors, for instance).
What was slightly more surprising to me was that for floats, the loop was faster than the linear reduction.
Looking at [godbolt output][] for a hardcoded case shows that they all get vectorized (and the loop gets unrolled), just with slightly different load scheduling.

[godbolt output]: https://godbolt.org/z/e32CnV

Criterion produces really cool graphs.
Here's the results from the two cases:

![violin-i32](/images/2018-08-27-violin-i32.svg)
![violin-f32](/images/2018-08-27-violin-f32.svg)

I suspect if you want to compute the minimum of a *very* large list, you'll benefit from doing tree reductions on independent chunks in a loop.
