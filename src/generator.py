# generator.py
import ast

class CppGenerator(ast.NodeVisitor):
    def __init__(self):
        self.code = []
        self.indentation_level = 0
        self.headers = set()

    def indent(self):
        return " " * self.indentation_level * 4

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "requests":
                self.headers.add('"requests.hpp"')

    def visit_FunctionDef(self, node):
        return_type = self.visit(node.returns) if node.returns else "void"
        function_name = node.name
        args = [self.visit(arg) for arg in node.args.args]
        self.code.append(f"{return_type} {function_name}({', '.join(args)}) {{")
        self.indentation_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation_level -= 1
        self.code.append("}")

    def visit_arg(self, node):
        arg_type = self.visit(node.annotation)
        return f"{arg_type} {node.arg}"

    def visit_Name(self, node):
        if node.id == 'int':
            return 'int'
        elif node.id == 'str':
            self.headers.add("<string>")
            return 'std::string'
        elif node.id == 'dict':
            self.headers.add('"nlohmann/json.hpp"')
            return 'nlohmann::json'
        return node.id

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return f'"{node.value}"'
        return str(node.value)

    def visit_JoinedStr(self, node):
        return " + ".join([self.visit(value) for value in node.values])

    def visit_FormattedValue(self, node):
        return self.visit(node.value)

    def visit_Assign(self, node):
        target = self.visit(node.targets[0])
        value = self.visit(node.value)
        if "requests::get" in value:
            self.headers.add('"cpr/cpr.h"')
            var_type = "cpr::Response"
        else:
            var_type = "int"

        self.code.append(f"{self.indent()}{var_type} {target} = {value};")

    def visit_Call(self, node):
        func = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        if func == "requests.get":
            return f"requests::get({', '.join(args)})"
        elif func.endswith(".json"):
            obj = func.replace(".json", "")
            self.headers.add('"nlohmann/json.hpp"')
            return f"nlohmann::json::parse({obj}.text)"
        return f"{func}({', '.join(args)})"

    def visit_Attribute(self, node):
        value = self.visit(node.value)
        return f"{value}.{node.attr}"

    def visit_Return(self, node):
        value = self.visit(node.value)
        self.code.append(f"{self.indent()}return {value};")

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        op = self.visit(node.op)
        right = self.visit(node.right)
        return f"{left} {op} {right}"

    def visit_Add(self, node):
        return "+"

    def visit_Sub(self, node):
        return "-"

    def visit_Mult(self, node):
        return "*"

    def visit_Div(self, node):
        return "/"

    def visit_If(self, node):
        test = self.visit(node.test)
        self.code.append(f"{self.indent()}if ({test}) {{")
        self.indentation_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation_level -= 1
        if node.orelse:
            self.code.append(f"{self.indent()}}} else {{")
            self.indentation_level += 1
            for stmt in node.orelse:
                self.visit(stmt)
            self.indentation_level -= 1
            self.code.append(f"{self.indent()}}}")
        else:
            self.code.append(f"{self.indent()}}}")

    def visit_Compare(self, node):
        left = self.visit(node.left)
        op = self.visit(node.ops[0])
        right = self.visit(node.comparators[0])
        return f"{left} {op} {right}"

    def visit_Gt(self, node):
        return ">"

    def visit_Lt(self, node):
        return "<"

    def visit_Eq(self, node):
        return "=="

    def visit_NotEq(self, node):
        return "!="

    def visit_GtE(self, node):
        return ">="

    def visit_LtE(self, node):
        return "<="

    def visit_Subscript(self, node):
        value = self.visit(node.value)
        slice = self.visit(node.slice)
        if value == "list":
            self.headers.add("<vector>")
            return f"std::vector<{slice}>"
        return f"{value}[{slice}]"

    def visit_For(self, node):
        target = self.visit(node.target)
        iter = self.visit(node.iter)
        # This is a simplification. We are assuming the type is `int`.
        self.code.append(f"{self.indent()}for (auto {target} : {iter}) {{")
        self.indentation_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation_level -= 1
        self.code.append(f"{self.indent()}}}")

    def visit_AugAssign(self, node):
        target = self.visit(node.target)
        op = self.visit(node.op)
        value = self.visit(node.value)
        self.code.append(f"{self.indent()}{target} {op}= {value};")

    def generate(self, node):
        self.visit(node)
        sorted_headers = sorted(list(self.headers))
        header_str = "\n".join([f"#include {h}" for h in sorted_headers])
        if header_str:
            return f"{header_str}\n\n" + "\n".join(self.code)
        return "\n".join(self.code)


def generate_cpp(ast_tree):
    generator = CppGenerator()
    return generator.generate(ast_tree)