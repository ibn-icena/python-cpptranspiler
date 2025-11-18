# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python to C++ transpiler that converts Python code with type annotations into equivalent C++ code. The transpiler uses Python's built-in AST (Abstract Syntax Tree) module to parse Python source files and generates C++ code through a visitor pattern.

## Architecture

The transpiler consists of three main components:

1. **Parser** (`src/parser.py`): Uses Python's `ast` module to parse Python source files into an AST
2. **Generator** (`src/generator.py`): Implements `CppGenerator`, an `ast.NodeVisitor` subclass that traverses the AST and generates corresponding C++ code
3. **Main** (`src/main.py`): CLI entry point that orchestrates the parsing and generation pipeline

### CppGenerator Design

The generator uses the visitor pattern to traverse Python AST nodes. Key implementation details:

- Each `visit_*` method handles a specific AST node type (e.g., `visit_FunctionDef`, `visit_If`, `visit_BinOp`)
- Automatically tracks required C++ headers in `self.headers` set (e.g., `<string>`, `<vector>`, `"cpr/cpr.h"`)
- Manages indentation levels to produce properly formatted C++ code
- Type mapping occurs during node visitation (e.g., Python `str` → C++ `std::string`, `list[int]` → `std::vector<int>`)

### Special Library Support

The transpiler has special handling for the `requests` library:
- Python `import requests` triggers inclusion of custom `requests.hpp` wrapper
- `requests.get()` calls are converted to use the CPR library (C++ Requests)
- Response objects are typed as `cpr::Response`
- `.json()` method calls are converted to `nlohmann::json::parse(response.text)`

## Development Commands

### Running the Transpiler

```bash
python -m src.main <path-to-python-file>
```

Example:
```bash
python -m src.main examples/simple.py
```

### Testing

Run all tests:
```bash
python -m unittest discover tests
```

Run a specific test file:
```bash
python -m unittest tests.test_parser
python -m unittest tests.test_generator
```

Run a single test:
```bash
python -m unittest tests.test_generator.TestGenerator.test_generate_simple_function
```

### Building C++ Output

The transpiler generates C++ code that depends on external libraries. To build the C++ code:

```bash
mkdir -p build
cd build
cmake ..
cmake --build .
```

The CMake configuration handles:
- CPR library for HTTP requests (vendored in `third_party/cpr`)
- nlohmann/json for JSON parsing (should be available in `third_party`)

## C++ Runtime Library

The `cpp_src/` directory contains runtime support headers:

- **`requests.hpp`**: Provides a Python-like `requests` namespace wrapping CPR library
  - `requests::get(url)` returns `cpr::Response`
  - Requires CPR library and nlohmann/json

## Type System

The transpiler requires Python type annotations to generate proper C++ types:

- `int` → `int`
- `str` → `std::string`
- `dict` → `nlohmann::json`
- `list[T]` → `std::vector<T>`

Functions must have parameter type annotations. Return type annotations are optional (defaults to `void`).

## Current Capabilities

The transpiler now supports:

**Core Language Features:**
- Function definitions with type annotations
- Classes with constructors (__init__) and methods
- Control flow: if/else, for loops, while loops
- Loop control: break, continue
- Binary operations: +, -, *, /
- Unary operations: +, -, ! (not)
- Comparisons: >, <, ==, !=, >=, <=
- Boolean operators: and (&&), or (||), not (!)
- Variable assignments and augmented assignments
- Function calls and method calls
- String literals and f-strings
- List subscripting and type annotations
- Print function (maps to std::cout)

**Python Standard Library Support:**
- `requests` module (via CPR library wrapper)
- `json` module (via nlohmann/json)
- `math` module (maps to <cmath>)
- `os` module (basic support via <filesystem>)
- `sys` module (partial support)

**Built-in Functions:**
- `print()` → `std::cout`
- `len()` → `.size()`
- `str()` → `std::to_string()`
- `int()` → `std::stoi()`

**String Methods:**
- `.upper()` → std::transform with ::toupper
- `.lower()` → std::transform with ::tolower

**List Methods:**
- `.append()` → `.push_back()`
- `.pop()` → `.pop_back()` or `.erase()`

**Class Support:**
- Class definitions with member variables
- Constructors (__init__ → ClassName constructor)
- Methods (self parameter automatically removed)
- Member variable type inference from constructor parameters

## Current Limitations

The transpiler does NOT yet support:
- Exception handling (try/except)
- Decorators
- Lambda functions
- Comprehensions (list/dict/set)
- Multiple return values / tuple unpacking
- Context managers (with statements)
- Generators and iterators
- Multiple inheritance
- Property decorators
- Static and class methods
- Advanced string methods (.split(), .join(), .strip(), etc.)
- Advanced list operations (slicing, .extend(), .insert(), etc.)
- Dictionary iteration and methods
- Set operations
- File I/O operations

## Adding Support for New Python Features

To add support for a new Python construct:

1. Add a `visit_<NodeType>` method to `CppGenerator` in `src/generator.py`
2. If the feature requires C++ headers, add them to `self.headers`
3. Add example Python file to `examples/`
4. Add corresponding test case to `tests/test_generator.py`
5. Update tests to verify both the AST parsing and C++ code generation
