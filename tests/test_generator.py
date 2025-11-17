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

if __name__ == "__main__":
    unittest.main()