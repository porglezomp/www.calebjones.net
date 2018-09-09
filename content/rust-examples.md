Title: Rust Examples
Date: 2016-10-29
Author: C Jones
Status: draft

# Optional Values

We define a type `OurOption` that's generic over some type `T`.
This means we can have specific types like `OurOption<String>` or `OurOption<i32>`.
`OurOption` gives us the semantics of "maybe we have a value, maybe not."

    ::rust
    enum OurOption<T> {

This is the "maybe we have a value" case.
Here we store some value of type T inside the Some variant.
Doing `Some(3i32)` will construct a value of type `OurOption<i32>` for example.

    ::rust
        Some(T),

None represents the "maybe not" case.
We have no value of type T to store, so we just store nothing.

    ::rust
        None,
    }

For reference, this might be written in C++ as:

    ::c++
    template <typename T>
    class OurOption {
        bool is_some;
        T value;
    };

And then leave value unintialized for the case where `is_some` is false.
It's obvious that it's less convenient to deal with the C++ version, since you have to do stuff like

    ::c++
    if (an_option.is_some()) {
        std::cout << an_option.unwrap() << std::endl;
    }

Instead of conveniences and safety like:

    ::rust
    if let Some(val) = an_option {
        println!("{}", val);
    }
    
# Error Handling

Here we have `OurResult`.
It's generic over two types this time, and encodes a notion of either success or failure on some operation.
We have two types so that we can have different things for our "error message."
A web request function might return `Result<String, HttpError>`, and some file-system functions do return `Result<File, fs::Error>`.

    ::rust
    enum OurResult<T, E> {

`Ok` stores values for the success case of the type.
`Ok(1)` represents that we computed the value 1, and we got it along the successful path.
If our function returned String error messages, then that `Ok(1)` might have the type `OurResult<i32, String>`.

    ::rust
        Ok(T),

Err stores values for the failure case of the type.
We can pass a value of type E which encodes the "reason," or just some extra information about the failure.
From our same example above, we might return Err("Failed to open file") when we can't read a number from the file, or Err("Invalid number format") if we can't parse a number.

    ::rust
        Err(E),
    }

Rust's power becomes even more evident here.
The naive implementation in C++ would look something like:

    ::c++
    template <typename T, typename E>
    class OurResult {
        bool is_ok;
        T ok;
        E err;
    };

The problem is, when `T` and `E` are large, we're wasting space storing both of them at the same time, when only one can be valid.
This means, in practice it will be implemented something more like:

    ::c++
    template <typename T, typename E>
    class OurResult {
        bool is_ok;
        union {
            T ok;
            E err;
        }
    };

Which reserves space for whichever of `T` or `E` is larger, and stores a single one of them at a time aligned at the beginning of that slot.
Writing stuff to work with this is even more complicated and error prone, and more enums only get worse from here.

# Sequencing Functions

`impl` lets us write code associated with a given type.

    ::rust
    impl<T> OurOption<T> {

`map` provides a notion of applying a function to a value that's inside a container.
If `OurOption` is `Some`, we'll apply the function to the thing inside.
If it's `None`, we just have to return `None`.

    ::rust
        fn map<F, O>(self, f: F) -> OurOption<O>
            // This is a constraint on the generic type F, it has to be a function
            // that accepts a value of type T and returns a value of type O.
            where F: Fn(T) -> O
        {
            match self {
                // f(x) produces an O, so we have to wrap it back in a Some
                OurOption::Some(x) => OurOption::Some(f(x)),
                OurOption::None => OurOption::None,
            }
        }

`and_then` provides a notion of sequencing operations that might not return a result.
Instead of applying a function to the value inside the container like `map` does, this will attempt to take the value out and just apply the function to the value inside the container.
The function here might not return a result.

    ::rust
        fn map<F, O>(self, f: F) -> OurOption<O>
            where F: Fn(T) -> OurOption<O>
        {
            match self {
                // Since f(x) returns an OurOption, we can just directly return it
                OurOption::Some(x) => f(x),
                OurOption::None => OurOption::None,
            }
        }
    }
    
# Demo
    
Division has a pole, it will fail when the denominator is zero.
Since we defined our nice operations on `OurOption`, we'll use `OurOption<f64>` to represent the type.
It is potentially more correct to use something like `OurResult<f64, ()>` or `OurResult<f64, SomeErrorType>`, but we don't have `map` or `and_then` for `OurResult`.

    ::rust
    fn maybe_divide(a: f64, b: f64) -> f64 {
        if b == 0.0 {
            None
        } else {
            Some(a / b)
        }
    }
    
We can use this like so:

    ::rustfn
    main() {
        // maybe_divide returns an OurOption here
        let res = maybe_divide(1.0, 3.0)
            // So we can use the and_then method we defined to call it again on the
            // value inside the container (if there is one).
            .and_then(|x| maybe_divide(x, 4.0))
            // Subtracting 3.0 can't fail, so we can use map here.
            .map(|x| x - 3.0)
            .and_then(|x| maybe_divide(5.0, x));

        match res {
            Some(val) => println!("Cool, we got: {}!", val),
            None => println!("Oops! Something went wrong!"),
        }
    }
