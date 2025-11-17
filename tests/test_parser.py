# test_parser.py
import ast
import unittest
from src.parser import parse_file

class TestParser(unittest.TestCase):
    def test_parse_file(self):
        ast_tree = parse_file("examples/simple.py")
        self.assertIsInstance(ast_tree, ast.AST)

if __name__ == "__main__":
    unittest.main()