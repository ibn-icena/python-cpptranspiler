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

if __name__ == "__main__":
    unittest.main()