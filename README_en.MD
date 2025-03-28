# Sobrecargar

[![Made by Chaska](https://img.shields.io/badge/made_by-Ch'aska-303030.svg)](https://cajadeideas.ar)
[![Version: 3.1.3](https://img.shields.io/badge/version-v3.1.3-green.svg)](https://github.com/hernanatn/github.com/hernanatn/sobrecargar.py/releases/latest)
[![Versión de Python: 3.9+](https://img.shields.io/badge/Python-3.9_%7C_3.10_%7C_3.11_%7C_3.12_%7C_3.13_%7C_3.14-blue?logo=python)](https://www.python.org/downloads/release/python-3120/)
[![License: MIT](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)


| Language  | Docs   | 
| :---- | ----: |
| :argentina: :es: | [/REAMDE.MD](/README.MD)   |
| :us: | [/REAMDE_en.MD](/README.MD)   |


## Description

`sobrecargar` is a Python module that implements a universal @decorator, allowing the definition of multiple versions of a function or method with different parameter sets and types. This enables function overloading similar to that found in languages like C++, but adapted to the spirit of Python.

### **Why Use Sobrecargar?**  

Python does not natively support function overloading, requiring alternative approaches such as:  

- **`*args` and `**kwargs` with manual type checking**  
- **Writing separate functions for different cases**  
- **Using `typing.overload`, which only provides static validation but does not affect runtime behavior**  

Sobrecargar eliminates repetitive code and improves safety by enforcing strict type checks at runtime.  

✅ **Concise** – Define multiple overloads with a simple decorator.  
✅ **Safe** – Enforces strict runtime type checking.  
✅ **Efficient** – Uses caching to minimize the cost of dynamic dispatch.  
✅ **Ergonomic** – Supports class method overloading without requiring redundant class definitions.  

## Installation

You can download and install `sobrecargar` using the `pip` package manager:

```bash
pip install sobrecargar
```

## Basic Usage

### Decorating a Function

You can use either `@sobrecargar` or its alias `@overload` to decorate functions:

```python
from sobrecargar import sobrecargar

@sobrecargar
def process(value: int):
    print(f"Processing an integer: {value}")

@sobrecargar
def process(value: str):
    print(f"Processing a string: {value}")

process(42)      # Processing an integer: 42
process("Hello")  # Processing a string: Hello
```

### Decorating a Class Method

> [!TIP]  
> Since version 3.0.2, methods (member functions) are *overloaded* in the same way as "free functions".

```python
from sobrecargar import sobrecargar

class MyClass:
    @sobrecargar
    def show(self, value: int):
        print(f"Received integer: {value}")

    @sobrecargar
    def show(self, value: str):
        print(f"Received string: {value}")

obj = MyClass()
obj.show(10)     # Received integer: 10
obj.show("Hello") # Received string: Hello
```

## More Complex Examples

### 'Free' Function

```python
@sobrecargar
def add(a: int, b: int):
    return a + b

@sobrecargar
def add(a: list[int]):
    return sum([x for x in a])

result1 = add(1, 2)         # Calls the first version: 3
result2 = add([1,2,3,4,5])  # Calls the second version: 15
```

### Example with Cache and Debugging

```python
@sobrecargar(cache=True, debug=True)
def calculate(a: float, *args: int):
    return a * sum(args)

@sobrecargar  # cache=True and debug=True are inherited from the first overload
def calculate(a: float, b: float):
    return a * b

floats: Iterable[tuple[float,float]] = ...
for a,b in floats: 
    calculate(a,b)  # In this scenario, the overload resolution logic
                   # is only executed on the first iteration of the loop,
                   # subsequent calls only incur the cost of
                   # looking up the overload cache.
```

## Configuration

The `@sobrecargar` decorator accepts the following configuration parameters:

| Parameter | Description | Default Value | Since Version |
|-----------|-------------|------------------|--------------|
| `cache` | If `True`, uses cache for overload resolution. The cache is sensitive not only to the types of the parameters but also to the order in which they were provided. | `True` | 3.1.X |
| `debug` | If `True`, prints debug messages to the console for: new overload registration, function call, cache (if any), and candidate resolution. | `False` | 3.1.X |

> [!NOTE]
> If any of the overloads declares a configuration parameter, it applies to all of them.

## Comparison with Other Approaches

| Approach | Advantages | Disadvantages |
|---------|----------|-------------|
| **Separate Functions** (`func_int()`, `func_str()`) | Explicit and clear | Code duplication, difficult to scale |
| **`*args` and `**kwargs` with `isinstance`** | Flexible | Requires manual type checking, prone to errors |
| **`typing.overload`** | Helps with static validation | Does not affect actual execution, only for tools |
| **`singledispatch`** | Supported by the standard library | Limited to dispatch on a single parameter |
| **`@sobrecargar`** | Easy to use, ensures type safety and flexibility | Slight runtime overhead |

## VSCode/VSCodium Extension

To enhance the development experience with `sobrecargar`, we offer an official extension for Visual Studio Code and VSCodium that provides integration with the Language Server Protocol (LSP).

[![VSCode/VSCodium Extension](https://img.shields.io/badge/VSCode-Official_Extension-007ACC?logo=visual-studio-code)](https://open-vsx.org/vscode/item?itemName=hernanatn.sobrecargar-vscode)

### Extension Features

- **Documentation**: Displays detailed information about each overload when hovering
- **Navigation**: Allows jumping between different implementations of an overloaded function

### Installation

You can install the extension directly from the VSCode/VSCodium marketplace:

1. Open VSCode/VSCodium
2. Go to the extensions tab (Ctrl+Shift+X)
3. Search for "sobrecargar" and install it

Alternatively, you can download it from [Open VSX Registry](https://open-vsx.org/vscode/item?itemName=hernanatn.sobrecargar-vscode)

## Documentation

This document provides high-level documentation on the public interface of `@sobrecargar`. For more details on implementation and advanced usage, please refer to the [full documentation](/docs) or explore the source code in the repository.

## Motivation

### Python Typing and Function Overloading

Python's dynamic typing, especially its "duck-typing" philosophy, is one of the language's most valuable features. The ability to rely on the interpreter to "keep going" without strict type constraints makes development in Python a fast, dynamic, and enriching experience, favoring rapid iteration.

However, dynamic typing comes at a cost: statically analyzing the **correctness** of a program becomes significantly more difficult. It is very challenging for a programmer to maintain the mental model of all possible runtime types that a piece of code is handling, at every step of the control flow branches for all possible program states.

Both the Python Software Foundation and the community at large have taken note of this trade-off and introduced numerous language features, libraries, and tools to address it. Python projects benefit from the existence of type hints, type checkers, runtime reflection libraries, etc.

Many typed Python projects eventually encounter use cases for polymorphic functions and methods. Function overloading is not just a convenience but a necessity for many practical cases.

### Current State of Overloading in Python

We can view overloading as a bridge between Python's duck-typing philosophy and type hints: it reintroduces the ability to "not worry so much about types" at the call site and facilitates the "keep going" approach, while allowing the developer to reap the benefits of types.

However, the current support for this pattern is lacking. It is true that many libraries expose APIs that are "overloaded beyond recognition," so that *it is often impossible to determine what they support and what they do not without guessing*. This is a problem with the implementation of the pattern, not the pattern itself.

**The biggest problem with `typing.overload`** is that it lies. It provides *hints* for multiple signatures but does not guarantee anything about the implementation that must actually handle them. In fact, calling code with `typing.overload` often leads to a great deal of effort trying to understand ad hoc type checks within catch-all implementations that may (and often do) simply not handle the set of cases their signatures say they should.

`singledispatch` attempts to address this, but it works for a very limited set of use cases and introduces a typing syntax that differs from the established type hint syntax.

### Our Solution

Typed Python is here to stay, and within typed codebases, the overloading pattern offers many advantages. The proof is in the fact that, even with the current state of support, overloading is widely used in both the standard library and popular third-party libraries.

`sobrecargar` offers an implementation of the pattern that:

- Guarantees type correctness
- Simplifies the definition of overloads
- Applies a consistent set of rules for overload selection
- Offers a better debugging experience
- Minimizes performance overhead


