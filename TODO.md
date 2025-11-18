# Python-to-C++ Transpiler - Feature Roadmap

## 📋 Implementation Status

Legend:
- ✅ Completed
- 🚧 In Progress
- ⏳ Planned
- ⏸️ On Hold

---

## 🔥 PACKAGE A: Quick Wins (Estimated: 3 hours)

High-value, low-effort features for immediate productivity boost.

### 1. Lambda Functions ⏳
**Priority:** HIGH | **Effort:** 30 min | **Impact:** ⭐⭐⭐⭐⭐

```python
lambda x: x * 2
lambda x, y: x + y
```
→
```cpp
[](int x) { return x * 2; }
[](int x, int y) { return x + y; }
```

**Implementation:**
- [ ] Add `visit_Lambda()` method
- [ ] Handle parameter inference
- [ ] Handle return type inference
- [ ] Support capture by value/reference
- [ ] Add tests

---

### 2. String Methods ⏳
**Priority:** HIGH | **Effort:** 1 hour | **Impact:** ⭐⭐⭐⭐⭐

**2a. String.split()** ⏳
```python
s.split(",")
s.split()  # whitespace
```
→
```cpp
// Custom split function or boost::split
```

**2b. String.strip()** ⏳
```python
s.strip()
s.lstrip()
s.rstrip()
```
→
```cpp
// Custom trim functions
```

**2c. String.join()** ⏳
```python
",".join(items)
```
→
```cpp
// Custom join with stringstream
```

**2d. String.replace()** ⏳
```python
s.replace("old", "new")
```
→
```cpp
// Use regex_replace or custom function
```

**2e. String.startswith/endswith()** ⏳
```python
s.startswith("prefix")
s.endswith("suffix")
```
→
```cpp
str.substr(0, prefix.length()) == prefix
```

**Implementation:**
- [ ] Create `cpp_src/string_utils.hpp` with utility functions
- [ ] Add method detection in `visit_Call()`
- [ ] Handle all 5 string methods
- [ ] Add comprehensive tests
- [ ] Add example file

---

### 3. Dictionary Iteration ⏳
**Priority:** HIGH | **Effort:** 30 min | **Impact:** ⭐⭐⭐⭐

```python
for key, value in dict.items():
for key in dict.keys():
for value in dict.values():
```
→
```cpp
for (auto& [key, value] : map) {
for (auto& key : map | std::views::keys) {  // C++20
for (auto& value : map | std::views::values) {
```

**Implementation:**
- [ ] Detect `.items()`, `.keys()`, `.values()` patterns
- [ ] Handle tuple unpacking in for loops
- [ ] Add `<map>` or use `nlohmann::json`
- [ ] Add tests

---

### 4. More List Methods ⏳
**Priority:** MEDIUM | **Effort:** 30 min | **Impact:** ⭐⭐⭐

**4a. list.extend()** ⏳
```python
list1.extend(list2)
```
→
```cpp
list1.insert(list1.end(), list2.begin(), list2.end());
```

**4b. list.insert()** ⏳
```python
list.insert(index, value)
```
→
```cpp
list.insert(list.begin() + index, value);
```

**4c. list.remove()** ⏳
```python
list.remove(value)
```
→
```cpp
list.erase(std::remove(list.begin(), list.end(), value), list.end());
```

**4d. list.index()** ⏳
```python
idx = list.index(value)
```
→
```cpp
auto it = std::find(list.begin(), list.end(), value);
int idx = std::distance(list.begin(), it);
```

**4e. list.count()** ⏳
```python
n = list.count(value)
```
→
```cpp
int n = std::count(list.begin(), list.end(), value);
```

**Implementation:**
- [ ] Add all 5 methods to `visit_Call()`
- [ ] Add `<algorithm>` header when needed
- [ ] Add tests for each method

---

## 💎 PACKAGE B: High Impact (Estimated: 9 hours)

Essential features for robust, real-world code.

### 5. List Comprehensions ⏳
**Priority:** HIGH | **Effort:** 2 hours | **Impact:** ⭐⭐⭐⭐⭐

```python
[x**2 for x in range(10)]
[x for x in items if x > 0]
[x*y for x in range(3) for y in range(3)]
```
→
```cpp
std::vector<int> result;
for (int x = 0; x < 10; x++) {
    result.push_back(x * x);
}
```

**Implementation:**
- [ ] Add `visit_ListComp()` method
- [ ] Handle generators (for clauses)
- [ ] Handle conditions (if clauses)
- [ ] Handle nested comprehensions
- [ ] Type inference for result vector
- [ ] Add tests

---

### 6. Exception Handling ⏳
**Priority:** HIGH | **Effort:** 3 hours | **Impact:** ⭐⭐⭐⭐⭐

```python
try:
    risky_operation()
except ValueError as e:
    handle_error(e)
except Exception as e:
    print(e)
finally:
    cleanup()
```
→
```cpp
try {
    risky_operation();
} catch (const std::invalid_argument& e) {
    handle_error(e);
} catch (const std::exception& e) {
    std::cout << e.what() << std::endl;
}
cleanup(); // finally
```

**Exception Mapping:**
- `ValueError` → `std::invalid_argument`
- `TypeError` → `std::bad_cast`
- `KeyError` → `std::out_of_range`
- `IndexError` → `std::out_of_range`
- `RuntimeError` → `std::runtime_error`
- `Exception` → `std::exception`

**Implementation:**
- [ ] Add `visit_Try()` method
- [ ] Add `visit_ExceptHandler()` method
- [ ] Map Python exceptions to C++ equivalents
- [ ] Handle `as` variable binding
- [ ] Handle finally blocks
- [ ] Add `raise` statement support
- [ ] Add tests

---

### 7. File I/O ⏳
**Priority:** HIGH | **Effort:** 2 hours | **Impact:** ⭐⭐⭐⭐

```python
with open("file.txt", "r") as f:
    content = f.read()

with open("out.txt", "w") as f:
    f.write("data")
```
→
```cpp
{
    std::ifstream f("file.txt");
    std::string content((std::istreambuf_iterator<char>(f)),
                         std::istreambuf_iterator<char>());
}

{
    std::ofstream f("out.txt");
    f << "data";
}
```

**File Methods:**
- `f.read()` → full file read
- `f.read(n)` → read n bytes
- `f.readline()` → `std::getline()`
- `f.readlines()` → read all lines to vector
- `f.write(s)` → stream output

**Implementation:**
- [ ] Add `visit_With()` for context managers
- [ ] Handle `open()` function
- [ ] Map file modes (r, w, a, rb, wb)
- [ ] Implement file methods
- [ ] Add `<fstream>` header
- [ ] RAII pattern for file handles
- [ ] Add tests

---

### 8. Tuple Unpacking / Multiple Returns ⏳
**Priority:** HIGH | **Effort:** 2 hours | **Impact:** ⭐⭐⭐⭐

```python
x, y = get_coords()
a, b, c = (1, 2, 3)
x, y = y, x  # swap
```
→
```cpp
auto [x, y] = get_coords();  // C++17 structured bindings
auto [a, b, c] = std::make_tuple(1, 2, 3);
std::swap(x, y);
```

**Implementation:**
- [ ] Detect tuple unpacking in assignments
- [ ] Generate structured bindings (C++17)
- [ ] Handle function returns as tuples
- [ ] Handle swap idiom
- [ ] Add tests

---

## 🎨 PACKAGE C: Complete Coverage (Estimated: 12+ hours)

Advanced features for comprehensive Python compatibility.

### 9. List/String Slicing ⏳
**Priority:** MEDIUM | **Effort:** 3 hours | **Impact:** ⭐⭐⭐⭐

```python
arr[1:5]      # range
arr[::2]      # step
arr[::-1]     # reverse
arr[:-1]      # negative indices
s[1:10]       # string slicing
```
→
```cpp
// Custom slice helper or std::span (C++20)
std::vector(arr.begin() + 1, arr.begin() + 5)
```

**Implementation:**
- [ ] Add `visit_Slice()` method
- [ ] Handle start:stop:step syntax
- [ ] Handle negative indices
- [ ] Handle omitted parameters
- [ ] Work with both lists and strings
- [ ] Create `cpp_src/slice_utils.hpp`
- [ ] Add tests

---

### 10. Enumerate & Zip ⏳
**Priority:** MEDIUM | **Effort:** 1 hour | **Impact:** ⭐⭐⭐

```python
for i, val in enumerate(arr):
for a, b in zip(list1, list2):
```
→
```cpp
for (size_t i = 0; i < arr.size(); i++) {
    auto val = arr[i];
}

// C++20 ranges or custom zip
```

**Implementation:**
- [ ] Detect `enumerate()` pattern
- [ ] Detect `zip()` pattern
- [ ] Generate appropriate for loops
- [ ] Handle tuple unpacking
- [ ] Add tests

---

### 11. Dict Comprehensions ⏳
**Priority:** MEDIUM | **Effort:** 1 hour | **Impact:** ⭐⭐⭐

```python
{k: v**2 for k, v in items.items()}
{x: x**2 for x in range(10)}
```
→
```cpp
std::map<KeyType, ValueType> result;
for (auto& [k, v] : items) {
    result[k] = v * v;
}
```

**Implementation:**
- [ ] Add `visit_DictComp()` method
- [ ] Similar to list comprehensions
- [ ] Use `std::map` or `nlohmann::json`
- [ ] Add tests

---

### 12. Set Operations ⏳
**Priority:** MEDIUM | **Effort:** 1 hour | **Impact:** ⭐⭐⭐

```python
s = {1, 2, 3}
s.add(4)
s.remove(3)
s.union(other)
s.intersection(other)
s.difference(other)
```
→
```cpp
std::set<int> s = {1, 2, 3};
s.insert(4);
s.erase(3);
std::set_union(...)
```

**Implementation:**
- [ ] Add set literal support
- [ ] Add set methods
- [ ] Use `<set>` or `<unordered_set>`
- [ ] Add tests

---

### 13. Regex Support ⏳
**Priority:** MEDIUM | **Effort:** 2 hours | **Impact:** ⭐⭐⭐

```python
import re
pattern = re.compile(r'\d+')
matches = pattern.findall(text)
if re.match(pattern, text):
```
→
```cpp
#include <regex>
std::regex pattern(R"(\d+)");
std::smatch matches;
std::regex_search(text, matches, pattern);
```

**Implementation:**
- [ ] Add `re` module support
- [ ] Map `re.compile()`, `re.match()`, `re.search()`
- [ ] Map `re.findall()`, `re.sub()`
- [ ] Add `<regex>` header
- [ ] Add tests

---

### 14. Enhanced f-strings ⏳
**Priority:** LOW | **Effort:** 1 hour | **Impact:** ⭐⭐⭐

```python
f"{value:.2f}"
f"{name:>10}"
f"{x=}"  # Debug format
```
→
```cpp
std::format("{:.2f}", value)  // C++20
// or use fmt library
```

**Implementation:**
- [ ] Parse format specifications
- [ ] Use std::format (C++20) or fmt library
- [ ] Handle all format types
- [ ] Add tests

---

### 15. Range Function ⏳
**Priority:** MEDIUM | **Effort:** 30 min | **Impact:** ⭐⭐⭐

```python
range(10)
range(5, 10)
range(0, 10, 2)
```
→
```cpp
// Custom range or use std::views::iota (C++20)
for (int i = 0; i < 10; i++)
```

**Implementation:**
- [ ] Detect `range()` in for loops
- [ ] Generate appropriate loop bounds
- [ ] Handle all three forms
- [ ] Add tests

---

## 📊 Implementation Progress

### Current Status
- ✅ Total Features Implemented: 80+
- ✅ Package A: 0/4 complete
- ✅ Package B: 0/4 complete
- ✅ Package C: 0/7 complete

### Next Steps
1. Start with Package A (Quick Wins)
2. Move to Package B (High Impact)
3. Complete Package C (Full Coverage)

---

## 🎯 Success Metrics

**Package A Complete:**
- 4 new features
- ~20 new tests
- Covers 70% of common Python patterns

**Package B Complete:**
- 8 total features
- ~35 new tests
- Covers 85% of common Python patterns

**Package C Complete:**
- 15 total features
- ~50 new tests
- Covers 95% of common Python patterns

---

## 📝 Notes

- Each feature should have at least 2 tests
- Each feature should have an example file
- Update CLAUDE.md after each package
- Commit after each major feature
- All tests must pass before moving to next feature

---

Last Updated: 2025-01-18
