# parser.py
import ast

def parse_file(file_path: str) -> ast.AST:
    """
    Parses a Python file and returns the AST.
    """
    with open(file_path, "r") as f:
        return ast.parse(f.read(), filename=file_path)