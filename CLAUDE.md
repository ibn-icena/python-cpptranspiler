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
- **Async functions** (async def) with C++20 coroutines - **NEW**
- **Lambda functions** → C++ lambdas with auto parameters - **NEW**
- **List comprehensions** with filters and nesting → IIFE pattern - **NEW**
- **Exception handling** (try/except/finally/raise) → C++ try/catch - **NEW**
- Classes with constructors (__init__) and methods
- Control flow: if/else, for loops, while loops
- Loop control: break, continue
- Binary operations: +, -, *, /, %, ** (power) - **% and ** NEW**
- Unary operations: +, -, ! (not)
- Comparisons: >, <, ==, !=, >=, <=
- Boolean operators: and (&&), or (||), not (!)
- Variable assignments and augmented assignments
- Function calls and method calls
- String literals and f-strings
- List and Tuple literals
- List subscripting and type annotations
- Multi-dimensional array indexing
- Print function (maps to std::cout)
- **Await expressions** (co_await) - **NEW**

**Python Standard Library Support:**
- `requests` module (via CPR library wrapper)
- `json` module (via nlohmann/json)
- `math` module (maps to <cmath>)
- `os` module (basic support via <filesystem>)
- `sys` module (partial support)
- **`numpy` module** (via NumCpp library) - **COMPREHENSIVE SUPPORT - NEW**
- **`multiprocessing` module** (via C++ threading) - **NEW**
- **`asyncio` module** (via C++20 coroutines) - **NEW**

**NumPy/NumCpp Support - NEW:**

Array Creation:
- `np.array([1,2,3])` → `nc::NdArray<T>({1,2,3})` with intelligent type inference
- `np.zeros(n)`, `np.ones(n)`, `np.arange()`, `np.linspace()`, `np.eye()`
- `np.random.rand()`, `np.random.randn()`

Mathematical Operations:
- Basic: `np.sum()`, `np.mean()`, `np.std()`, `np.min()`, `np.max()`
- Advanced: `np.dot()`, `np.matmul()`, `np.sqrt()`, `np.exp()`, `np.log()`, `np.abs()`
- Analysis: `np.argmax()`, `np.argmin()`, `np.where()`

Array Manipulation:
- Stack/Combine: `np.concatenate()`, `np.vstack()`, `np.hstack()`, `np.stack()`
- Transform: `arr.reshape()`, `arr.transpose()`, `arr.T`
- Properties: `arr.shape`, `arr.size` (auto-converted to method calls)
- Indexing: Multi-dimensional `arr[i,j]` → `arr(i,j)`

Linear Algebra (np.linalg):
- `det()` - determinant
- `inv()` - matrix inverse
- `eig()` - eigenvalues/eigenvectors
- `solve()` - solve linear systems
- `svd()` - singular value decomposition
- `norm()` - matrix/vector norms

Type Inference:
- Automatic int vs double detection: `[1,2,3]` → `NdArray<int>`, `[1.0,2.0]` → `NdArray<double>`
- Mixed types promote to double: `[1,2.0,3]` → `NdArray<double>`

**Multiprocessing Support - NEW:**
- `Process(target=func, args=(...))` → `std::thread(func, ...)`
- `Lock()` → `std::mutex`
- `thread.join()` → `thread.join()`
- Automatic type inference for std::thread and std::mutex
- **Note:** Python uses processes (separate memory), C++ uses threads (shared memory)

**Async/Await Support (Requires C++20) - NEW:**
- `async def func() -> T` → `Task<T> func()`
- `await expr` → `co_await expr`
- `return value` → `co_return value` in async functions
- Full coroutine infrastructure with Task<T> wrapper (cpp_src/task.hpp)
- Exception propagation through coroutines
- Both `Task<T>` and `Task<void>` supported
- **Note:** C++20 coroutines differ from Python's event loop model

**Built-in Functions:**
- `print()` → `std::cout`
- `len()` → `.size()`
- `str()` → `std::to_string()`
- `int()` → `std::stoi()`
- **`range(n)`, `range(start, stop)`, `range(start, stop, step)`** → vector-based range generation - **NEW**

**List Comprehensions:** - **NEW**
- Basic: `[x**2 for x in range(10)]` → IIFE with vector building loop
- With filter: `[x for x in nums if x > 0]` → nested if inside loop
- Nested: `[[i*j for j in range(3)] for i in range(3)]` → nested IIFEs
- Supports arbitrary expressions and multiple filters
- Power operator `**` → `std::pow(base, exp)`
- Modulo operator `%` → `%`

**Exception Handling:** - **NEW**
- Try/Except: `try: ... except ExceptionType: ...` → `try { ... } catch (const std::exception&) { ... }`
- Exception with variable: `except ValueError as e:` → `catch (const std::invalid_argument& e)`
- Catch-all: `except:` → `catch (...)`
- Finally block: `finally:` → code after all catch blocks (limited semantics)
- Raise exceptions: `raise ValueError("msg")` → `throw std::invalid_argument("msg")`
- Re-raise: `raise` → `throw;`
- Exception type mapping:
  - `Exception` → `std::exception`
  - `ValueError`, `TypeError` → `std::invalid_argument`
  - `RuntimeError` → `std::runtime_error`
  - `KeyError`, `IndexError` → `std::out_of_range`
  - `ZeroDivisionError` → `std::overflow_error`
  - `FileNotFoundError`, `IOError` → `std::runtime_error`
- **Note:** C++ finally doesn't have same semantics as Python (won't execute on uncaught exceptions)

**String Methods (via string_utils.hpp):** - **NEW**
- `.upper()` → std::transform with ::toupper
- `.lower()` → std::transform with ::tolower
- `.split(delimiter)` → `string_utils::split()`
- `.strip()`, `.lstrip()`, `.rstrip()` → `string_utils::strip/lstrip/rstrip()`
- `.join(items)` → `string_utils::join()`
- `.replace(old, new)` → `string_utils::replace()`
- `.startswith(prefix)`, `.endswith(suffix)` → `string_utils::startswith/endswith()`

**List Methods:**
- `.append()` → `.push_back()`
- `.pop()` → `.pop_back()` or `.erase()`
- `.extend(list2)` → `.insert(list.end(), list2.begin(), list2.end())` - **NEW**
- `.insert(index, value)` → `.insert(list.begin() + index, value)` - **NEW**
- `.remove(value)` → `.erase(std::remove(...), list.end())` - **NEW**
- `.index(value)` → `std::distance(..., std::find(...))` - **NEW**
- `.count(value)` → `std::count(...)` - **NEW**

**Dictionary Support:** - **NEW**
- Dictionary literals: `{"a": 1, "b": 2}` → `{{"a", 1}, {"b", 2}}`
- `.items()` iteration → C++17 structured bindings: `for (auto& [key, value] : dict)`
- `.keys()` iteration → `for (auto& _pair : dict) { auto key = _pair.first; }`
- `.values()` iteration → `for (auto& _pair : dict) { auto value = _pair.second; }`

**Class Support:**
- Class definitions with member variables
- Constructors (__init__ → ClassName constructor)
- Methods (self parameter automatically removed)
- Member variable type inference from constructor parameters

## Current Limitations

The transpiler does NOT yet support:
- Decorators
- Dict/Set comprehensions (list comprehensions are supported)
- Multiple return values / tuple unpacking
- Context managers (with statements)
- Generators and iterators
- Multiple inheritance
- Property decorators
- Static and class methods
- List/String slicing (subscripting works)
- Set operations
- File I/O operations

## Adding Support for New Python Features

To add support for a new Python construct:

1. Add a `visit_<NodeType>` method to `CppGenerator` in `src/generator.py`
2. If the feature requires C++ headers, add them to `self.headers`
3. Add example Python file to `examples/`
4. Add corresponding test case to `tests/test_generator.py`
5. Update tests to verify both the AST parsing and C++ code generation
