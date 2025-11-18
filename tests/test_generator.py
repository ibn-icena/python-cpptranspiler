# test_generator.py
import unittest
from src.parser import parse_file
from src.generator import generate_cpp

class TestGenerator(unittest.TestCase):
    def test_generate_simple_function(self):
        ast_tree = parse_file("examples/simple.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """int add(int a, int b) {
    return a + b;
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_if_else(self):
        ast_tree = parse_file("examples/if_else.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """int max(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_list(self):
        ast_tree = parse_file("examples/list.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """#include <vector>

int sum(std::vector<int> a) {
    int total = 0;
    for (int x : a) {
        total += x;
    }
    return total;
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_requests_example(self):
        ast_tree = parse_file("examples/requests_example.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """#include "requests.hpp"
#include <string>

nlohmann::json get_github_user(std::string username) {
    cpr::Response response = requests::get("https://api.github.com/users/" + username);
    return nlohmann::json::parse(response.text);
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_while_loop(self):
        ast_tree = parse_file("examples/while_loop.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """int countdown(int n) {
    while (n > 0) {
        n -= 1;
    }
    return n;
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_print(self):
        ast_tree = parse_file("examples/print_example.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """#include <iostream>
#include <string>

void greet(std::string name) {
    std::cout << "Hello" << " " << name << std::endl;
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_break_continue(self):
        ast_tree = parse_file("examples/break_continue.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """int find_first_positive(int n) {
    int i = 0;
    while (i < n) {
        i += 1;
        if (i < 0) {
            continue;
        }
        if (i > 10) {
            break;
        }
        return i;
    }
    return -1;
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_boolean_ops(self):
        ast_tree = parse_file("examples/boolean_ops.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """int is_valid(int x, int y) {
    if (x > 0 && y > 0) {
        return 1;
    }
    if (x < 0 || y < 0) {
        return -1;
    }
    if (!(x == y)) {
        return 0;
    }
    return 2;
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_class(self):
        ast_tree = parse_file("examples/class_example.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """class Counter {
public:
    int count;

    Counter(int start) {
        count = start;
    }
    int increment() {
        count += 1;
        return count;
    }
    int get_count() {
        return count;
    }
};"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_lambda(self):
        ast_tree = parse_file("examples/lambda_example.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """#include <iostream>

void test_lambdas() {
    auto double = [](auto x) { return x * 2; };
    int result1 = double(5);
    std::cout << result1 << std::endl;
    auto add = [](auto x, auto y) { return x + y; };
    int result2 = add(3, 4);
    std::cout << result2 << std::endl;
    auto multiply = [](auto a, auto b) { return a * b + 10; };
    int result3 = multiply(2, 3);
    std::cout << result3 << std::endl;
    return result1;
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_string_methods(self):
        ast_tree = parse_file("examples/string_methods_example.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """#include "string_utils.hpp"
#include <string>

void test_string_methods(std::string text) {
    auto words = string_utils::split(text, " ");
    auto csv_values = string_utils::split(text, ",");
    auto whitespace_split = string_utils::split(text);
    auto trimmed = string_utils::strip(text);
    auto left_trim = string_utils::lstrip(text);
    auto right_trim = string_utils::rstrip(text);
    auto joined = string_utils::join(",", words);
    auto replaced = string_utils::replace(text, "old", "new");
    auto starts = string_utils::startswith(text, "Hello");
    auto ends = string_utils::endswith(text, "world");
    return joined;
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_dict_iteration(self):
        ast_tree = parse_file("examples/dict_iteration_example.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """#include <iostream>
#include <map>

void test_dict_iteration() {
    auto data = {{"a", 1}, {"b", 2}, {"c", 3}};
    for (auto& [key, value] : data) {
        std::cout << key << " " << value << std::endl;
    }
    for (auto& _pair : data) {
        auto key = _pair.first;
        std::cout << key << std::endl;
    }
    for (auto& _pair : data) {
        auto value = _pair.second;
        std::cout << value << std::endl;
    }
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_list_methods(self):
        ast_tree = parse_file("examples/list_methods_example.py")
        cpp_code = generate_cpp(ast_tree)
        expected_code = """#include <algorithm>

void test_list_methods() {
    auto numbers = {1, 2, 3, 4, 5};
    auto more_numbers = {6, 7, 8};
    numbers.insert(numbers.end(), more_numbers.begin(), more_numbers.end());
    numbers.insert(numbers.begin() + 0, 0);
    numbers.erase(std::remove(numbers.begin(), numbers.end(), 3), numbers.end());
    int idx = std::distance(numbers.begin(), std::find(numbers.begin(), numbers.end(), 5));
    int count = std::count(numbers.begin(), numbers.end(), 2);
    return idx;
}"""
        self.assertEqual(cpp_code, expected_code)

    def test_generate_list_comprehension(self):
        ast_tree = parse_file("examples/list_comprehension_example.py")
        cpp_code = generate_cpp(ast_tree)
        # Just verify it contains the key elements
        self.assertIn("std::vector<int> _result", cpp_code)
        self.assertIn("std::pow(x, 2)", cpp_code)
        self.assertIn("x % 2 == 0", cpp_code)
        self.assertIn("<cmath>", cpp_code)
        self.assertIn("<vector>", cpp_code)

    def test_generate_exception_handling(self):
        ast_tree = parse_file("examples/exception_example.py")
        cpp_code = generate_cpp(ast_tree)
        # Verify key exception handling elements
        self.assertIn("<stdexcept>", cpp_code)
        self.assertIn("try {", cpp_code)
        self.assertIn("catch (const std::overflow_error&)", cpp_code)
        self.assertIn("catch (const std::out_of_range& e)", cpp_code)
        self.assertIn("catch (const std::exception& e)", cpp_code)
        self.assertIn("throw std::invalid_argument", cpp_code)
        self.assertIn("Cleanup", cpp_code)  # Finally block content

if __name__ == "__main__":
    unittest.main()