# main.py
import argparse
from src.parser import parse_file
from src.generator import generate_cpp

def main():
    parser = argparse.ArgumentParser(description="Python to C++ Transpiler")
    parser.add_argument("file", help="The Python file to transpile")
    args = parser.parse_args()

    ast_tree = parse_file(args.file)
    cpp_code = generate_cpp(ast_tree)
    print(cpp_code)

if __name__ == "__main__":
    main()