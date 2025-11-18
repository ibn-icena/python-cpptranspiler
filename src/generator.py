# generator.py
import ast

class CppGenerator(ast.NodeVisitor):
    def __init__(self):
        self.code = []
        self.indentation_level = 0
        self.headers = set()
        self.variable_types = {}  # Track variable types for type inference
        self.current_class = None  # Track current class name
        self.class_members = {}  # Track member variables by class
        self.async_functions = set()  # Track async functions
        self.current_function_is_async = False  # Track if currently in async function

    def indent(self):
        return " " * self.indentation_level * 4

    def infer_numpy_dtype(self, node):
        """Infer NumPy array dtype from list/tuple elements"""
        if isinstance(node, ast.List) or isinstance(node, ast.Tuple):
            has_float = False
            for elt in node.elts:
                if isinstance(elt, ast.Constant):
                    if isinstance(elt.value, float):
                        has_float = True
                    elif not isinstance(elt.value, int):
                        # Unknown type, default to double
                        return "double"
            return "double" if has_float else "int"
        return "double"  # Default

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "requests":
                self.headers.add('"requests.hpp"')
            elif alias.name == "json":
                self.headers.add('"nlohmann/json.hpp"')
            elif alias.name == "math":
                self.headers.add("<cmath>")
            elif alias.name == "os":
                self.headers.add("<filesystem>")
            elif alias.name == "sys":
                # sys module - no specific header, handled case-by-case
                pass
            elif alias.name == "numpy":
                self.headers.add('"NumCpp.hpp"')
                # Store the alias name (e.g., "np" if imported as "import numpy as np")
                if not hasattr(self, 'numpy_alias'):
                    self.numpy_alias = alias.asname if alias.asname else "numpy"
            elif alias.name == "multiprocessing":
                self.headers.add("<thread>")
                self.headers.add("<future>")
                self.headers.add("<vector>")
                self.headers.add("<mutex>")

    def visit_ImportFrom(self, node):
        # Handle "from module import ..." statements
        if node.module == "multiprocessing":
            self.headers.add("<thread>")
            self.headers.add("<future>")
            self.headers.add("<vector>")
            self.headers.add("<mutex>")
        elif node.module == "asyncio":
            self.headers.add("<coroutine>")
            self.headers.add('"task.hpp"')
            self.headers.add("<vector>")

    def visit_ClassDef(self, node):
        class_name = node.name
        self.current_class = class_name
        self.class_members[class_name] = []

        # Pre-pass: Find __init__ and collect member variables
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                # Temporarily process __init__ to collect member variables
                for stmt in item.body:
                    if isinstance(stmt, ast.Assign):
                        target = stmt.targets[0]
                        if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == "self":
                            member_name = target.attr
                            # Infer type from value
                            if isinstance(stmt.value, ast.Name):
                                # Look up parameter type
                                var_name = stmt.value.id
                                # Find the parameter in __init__
                                for arg in item.args.args[1:]:  # Skip self
                                    if arg.arg == var_name:
                                        var_type = self.visit(arg.annotation) if arg.annotation else "auto"
                                        self.class_members[class_name].append((member_name, var_type))
                                        break
                            elif isinstance(stmt.value, ast.Constant):
                                if isinstance(stmt.value.value, str):
                                    self.class_members[class_name].append((member_name, "std::string"))
                                elif isinstance(stmt.value.value, int):
                                    self.class_members[class_name].append((member_name, "int"))

        # Now generate the class
        self.code.append(f"class {class_name} {{")
        self.code.append("public:")
        self.indentation_level += 1

        # Add member variable declarations
        for member_name, member_type in self.class_members[class_name]:
            self.code.append(f"{self.indent()}{member_type} {member_name};")

        if self.class_members[class_name]:
            self.code.append("")  # Blank line after members

        # Process methods
        for item in node.body:
            self.visit(item)

        self.indentation_level -= 1
        self.code.append("};")
        self.current_class = None

    def visit_FunctionDef(self, node):
        # Check if this is a method (inside a class)
        is_method = self.current_class is not None
        is_constructor = is_method and node.name == "__init__"

        # For methods, skip the first parameter (self)
        args = node.args.args[1:] if is_method else node.args.args

        if is_constructor:
            # Constructor doesn't have return type
            function_name = self.current_class
            self.code.append(f"{self.indent()}{function_name}({', '.join([self.visit(arg) for arg in args])}) {{")
        else:
            # Check if function returns a tuple (scan for tuple returns)
            returns_tuple = self._function_returns_tuple(node)

            if returns_tuple:
                return_type = "auto"
                self.headers.add("<tuple>")
            else:
                return_type = self.visit(node.returns) if node.returns else "void"

            function_name = node.name
            args_str = ', '.join([self.visit(arg) for arg in args])
            if is_method:
                self.code.append(f"{self.indent()}{return_type} {function_name}({args_str}) {{")
            else:
                self.code.append(f"{return_type} {function_name}({args_str}) {{")

        self.indentation_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation_level -= 1
        self.code.append(f"{self.indent()}}}")

    def _function_returns_tuple(self, node):
        """Check if a function returns a tuple"""
        for stmt in ast.walk(node):
            if isinstance(stmt, ast.Return) and stmt.value and isinstance(stmt.value, ast.Tuple):
                return True
        return False

    def visit_AsyncFunctionDef(self, node):
        # Async function - generate C++20 coroutine
        self.headers.add("<coroutine>")
        self.headers.add('"task.hpp"')

        is_method = self.current_class is not None
        args = node.args.args[1:] if is_method else node.args.args

        return_type = self.visit(node.returns) if node.returns else "void"
        function_name = node.name
        args_str = ', '.join([self.visit(arg) for arg in args])

        # Mark this function as async
        self.async_functions.add(function_name)
        self.current_function_is_async = True

        # Wrap return type in Task<T>
        coroutine_return_type = f"Task<{return_type}>"

        if is_method:
            self.code.append(f"{self.indent()}{coroutine_return_type} {function_name}({args_str}) {{")
        else:
            self.code.append(f"{coroutine_return_type} {function_name}({args_str}) {{")

        self.indentation_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation_level -= 1
        self.code.append(f"{self.indent()}}}")

        self.current_function_is_async = False

    def visit_arg(self, node):
        arg_type = self.visit(node.annotation)
        self.variable_types[node.arg] = arg_type  # Track parameter types
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
        target_node = node.targets[0]

        # Check if this is tuple unpacking (x, y = ...)
        if isinstance(target_node, ast.Tuple):
            self.headers.add("<tuple>")
            # C++17 structured bindings
            vars = [self.visit(elt) for elt in target_node.elts]
            value = self.visit(node.value)
            self.code.append(f"{self.indent()}auto [{', '.join(vars)}] = {value};")
            return

        target = self.visit(target_node)
        value = self.visit(node.value)

        # Check if this is a member variable assignment (self.x = ...)
        if isinstance(target_node, ast.Attribute) and isinstance(target_node.value, ast.Name) and target_node.value.id == "self":
            member_name = target_node.attr
            # Track member variable
            if self.current_class:
                # Check if not already tracked
                member_exists = any(name == member_name for name, _ in self.class_members[self.current_class])
                if not member_exists:
                    # Infer type from the value
                    if "requests::get" in value:
                        var_type = "cpr::Response"
                    elif isinstance(node.value, ast.Constant):
                        if isinstance(node.value.value, str):
                            var_type = "std::string"
                        elif isinstance(node.value.value, int):
                            var_type = "int"
                        else:
                            var_type = "auto"
                    elif isinstance(node.value, ast.Name):
                        # If assigning from a variable, use its type
                        var_name = node.value.id
                        var_type = self.variable_types.get(var_name, "auto")
                    else:
                        var_type = "auto"
                    self.class_members[self.current_class].append((member_name, var_type))
            # Generate assignment
            self.code.append(f"{self.indent()}{target} = {value};")
        else:
            # Regular variable assignment
            if isinstance(node.value, ast.Dict):
                # Dictionary literal - use auto for type inference
                var_type = "auto"
            elif isinstance(node.value, ast.List):
                # List literal - use auto for type inference
                var_type = "auto"
            elif isinstance(node.value, ast.ListComp):
                # List comprehension - use auto for type inference
                var_type = "auto"
            elif isinstance(node.value, ast.Lambda):
                # Lambda functions should use auto
                var_type = "auto"
            elif value and "requests::get" in value:
                var_type = "cpr::Response"
            elif value and ("nc::" in value or ".reshape(" in value or ".transpose(" in value):
                # NumPy array - use auto for type inference
                var_type = "auto"
            elif value and "std::thread" in value:
                # Multiprocessing thread
                var_type = "std::thread"
            elif value and "std::mutex" in value:
                var_type = "std::mutex"
            elif value and "string_utils::" in value:
                # String utility functions - use auto for type inference
                var_type = "auto"
            elif value and ("std::istreambuf_iterator" in value or "std::getline" in value or "_lines" in value):
                # File operation results - use auto
                var_type = "auto"
            else:
                var_type = "int"
            self.code.append(f"{self.indent()}{var_type} {target} = {value};")

    def visit_Call(self, node):
        func = self.visit(node.func)
        args = [self.visit(arg) for arg in node.args]
        if func == "print":
            self.headers.add("<iostream>")
            if args:
                sep = ' << " " << '
                args_str = sep.join(args)
                return f"std::cout << {args_str} << std::endl"
            else:
                return "std::cout << std::endl"
        elif func == "len":
            return f"{args[0]}.size()"
        elif func == "str":
            return f"std::to_string({args[0]})"
        elif func == "int":
            return f"std::stoi({args[0]})"
        elif func == "range":
            # range() function for list comprehensions
            self.headers.add("<vector>")
            if len(args) == 1:
                # range(n) → generates 0 to n-1
                return f"[&](){{ std::vector<int> _r; for(int _i=0; _i<{args[0]}; _i++) _r.push_back(_i); return _r; }}()"
            elif len(args) == 2:
                # range(start, stop) → custom range generator
                return f"[&](){{ std::vector<int> _r; for(int _i={args[0]}; _i<{args[1]}; _i++) _r.push_back(_i); return _r; }}()"
            elif len(args) == 3:
                # range(start, stop, step)
                return f"[&](){{ std::vector<int> _r; for(int _i={args[0]}; _i<{args[1]}; _i+={args[2]}) _r.push_back(_i); return _r; }}()"
            return "std::vector<int>()"
        # Math module functions
        elif func.startswith("math."):
            math_func = func.replace("math.", "std::")
            return f"{math_func}({', '.join(args)})"
        # JSON module functions
        elif func == "json.loads":
            return f"nlohmann::json::parse({', '.join(args)})"
        elif func == "json.dumps":
            return f"{args[0]}.dump()"
        # Requests module
        elif func == "requests.get":
            return f"requests::get({', '.join(args)})"
        elif func.endswith(".json"):
            obj = func.replace(".json", "")
            # Only add nlohmann/json.hpp if we're not already using requests.hpp
            if '"requests.hpp"' not in self.headers:
                self.headers.add('"nlohmann/json.hpp"')
            return f"nlohmann::json::parse({obj}.text)"
        # String methods
        elif func.endswith(".upper"):
            obj = func.replace(".upper", "")
            self.headers.add("<algorithm>")
            self.headers.add("<cctype>")
            return f"std::transform({obj}.begin(), {obj}.end(), {obj}.begin(), ::toupper), {obj}"
        elif func.endswith(".lower"):
            obj = func.replace(".lower", "")
            self.headers.add("<algorithm>")
            self.headers.add("<cctype>")
            return f"std::transform({obj}.begin(), {obj}.end(), {obj}.begin(), ::tolower), {obj}"
        elif func.endswith(".split"):
            obj = func.replace(".split", "")
            self.headers.add('"string_utils.hpp"')
            if args:
                return f"string_utils::split({obj}, {args[0]})"
            else:
                return f"string_utils::split({obj})"
        elif func.endswith(".strip"):
            obj = func.replace(".strip", "")
            self.headers.add('"string_utils.hpp"')
            return f"string_utils::strip({obj})"
        elif func.endswith(".lstrip"):
            obj = func.replace(".lstrip", "")
            self.headers.add('"string_utils.hpp"')
            return f"string_utils::lstrip({obj})"
        elif func.endswith(".rstrip"):
            obj = func.replace(".rstrip", "")
            self.headers.add('"string_utils.hpp"')
            return f"string_utils::rstrip({obj})"
        elif func.endswith(".join"):
            obj = func.replace(".join", "")
            self.headers.add('"string_utils.hpp"')
            return f"string_utils::join({obj}, {args[0]})"
        elif func.endswith(".replace"):
            obj = func.replace(".replace", "")
            self.headers.add('"string_utils.hpp"')
            return f"string_utils::replace({obj}, {', '.join(args)})"
        elif func.endswith(".startswith"):
            obj = func.replace(".startswith", "")
            self.headers.add('"string_utils.hpp"')
            return f"string_utils::startswith({obj}, {args[0]})"
        elif func.endswith(".endswith"):
            obj = func.replace(".endswith", "")
            self.headers.add('"string_utils.hpp"')
            return f"string_utils::endswith({obj}, {args[0]})"
        # List methods
        elif func.endswith(".append"):
            obj = func.replace(".append", "")
            return f"{obj}.push_back({', '.join(args)})"
        elif func.endswith(".pop"):
            obj = func.replace(".pop", "")
            if args:
                # pop(index) - more complex, not implementing for now
                return f"{obj}.erase({obj}.begin() + {args[0]})"
            else:
                return f"{obj}.pop_back()"
        elif func.endswith(".extend"):
            obj = func.replace(".extend", "")
            self.headers.add("<algorithm>")
            return f"{obj}.insert({obj}.end(), {args[0]}.begin(), {args[0]}.end())"
        elif func.endswith(".insert"):
            obj = func.replace(".insert", "")
            return f"{obj}.insert({obj}.begin() + {args[0]}, {args[1]})"
        elif func.endswith(".remove"):
            obj = func.replace(".remove", "")
            self.headers.add("<algorithm>")
            return f"{obj}.erase(std::remove({obj}.begin(), {obj}.end(), {args[0]}), {obj}.end())"
        elif func.endswith(".index"):
            obj = func.replace(".index", "")
            self.headers.add("<algorithm>")
            # Returns index of first occurrence
            return f"std::distance({obj}.begin(), std::find({obj}.begin(), {obj}.end(), {args[0]}))"
        elif func.endswith(".count"):
            obj = func.replace(".count", "")
            self.headers.add("<algorithm>")
            return f"std::count({obj}.begin(), {obj}.end(), {args[0]})"
        # NumPy array creation functions
        elif func in ["np.array", "numpy.array"]:
            # np.array([1,2,3]) → nc::NdArray<int>({1,2,3})
            # Infer type from array elements
            dtype = self.infer_numpy_dtype(node.args[0]) if node.args else "double"
            return f"nc::NdArray<{dtype}>({args[0]})"
        elif func in ["np.zeros", "numpy.zeros"]:
            return f"nc::zeros<double>({', '.join(args)})"
        elif func in ["np.ones", "numpy.ones"]:
            return f"nc::ones<double>({', '.join(args)})"
        elif func in ["np.arange", "numpy.arange"]:
            return f"nc::arange<double>({', '.join(args)})"
        elif func in ["np.linspace", "numpy.linspace"]:
            return f"nc::linspace<double>({', '.join(args)})"
        elif func in ["np.eye", "numpy.eye"]:
            return f"nc::eye<double>({', '.join(args)})"
        # NumPy random functions
        elif func in ["np.random.rand", "numpy.random.rand"]:
            return f"nc::random::rand<double>(nc::Shape({', '.join(args)}))"
        elif func in ["np.random.randn", "numpy.random.randn"]:
            return f"nc::random::standardNormal<double>(nc::Shape({', '.join(args)}))"
        # NumPy mathematical functions (that take arrays)
        elif func in ["np.sum", "numpy.sum"]:
            return f"nc::sum({', '.join(args)})"
        elif func in ["np.mean", "numpy.mean"]:
            return f"nc::mean({', '.join(args)})"
        elif func in ["np.std", "numpy.std"]:
            return f"nc::stdev({', '.join(args)})"
        elif func in ["np.min", "numpy.min"]:
            return f"nc::min({', '.join(args)})"
        elif func in ["np.max", "numpy.max"]:
            return f"nc::max({', '.join(args)})"
        elif func in ["np.dot", "numpy.dot"]:
            return f"nc::dot({', '.join(args)})"
        elif func in ["np.sqrt", "numpy.sqrt"]:
            return f"nc::sqrt({', '.join(args)})"
        elif func in ["np.exp", "numpy.exp"]:
            return f"nc::exp({', '.join(args)})"
        elif func in ["np.log", "numpy.log"]:
            return f"nc::log({', '.join(args)})"
        elif func in ["np.abs", "numpy.abs"]:
            return f"nc::abs({', '.join(args)})"
        # Advanced NumPy functions
        elif func in ["np.matmul", "numpy.matmul"]:
            return f"nc::matmul({', '.join(args)})"
        elif func in ["np.argmax", "numpy.argmax"]:
            return f"nc::argmax({', '.join(args)})"
        elif func in ["np.argmin", "numpy.argmin"]:
            return f"nc::argmin({', '.join(args)})"
        elif func in ["np.where", "numpy.where"]:
            return f"nc::where({', '.join(args)})"
        elif func in ["np.concatenate", "numpy.concatenate"]:
            return f"nc::concatenate({', '.join(args)})"
        elif func in ["np.vstack", "numpy.vstack"]:
            return f"nc::vstack({', '.join(args)})"
        elif func in ["np.hstack", "numpy.hstack"]:
            return f"nc::hstack({', '.join(args)})"
        elif func in ["np.stack", "numpy.stack"]:
            return f"nc::stack({', '.join(args)})"
        # NumPy linalg module
        elif func in ["np.linalg.det", "numpy.linalg.det"]:
            return f"nc::linalg::det({', '.join(args)})"
        elif func in ["np.linalg.inv", "numpy.linalg.inv"]:
            return f"nc::linalg::inv({', '.join(args)})"
        elif func in ["np.linalg.eig", "numpy.linalg.eig"]:
            # Returns tuple, may need special handling
            return f"nc::linalg::eig({', '.join(args)})"
        elif func in ["np.linalg.solve", "numpy.linalg.solve"]:
            return f"nc::linalg::solve({', '.join(args)})"
        elif func in ["np.linalg.svd", "numpy.linalg.svd"]:
            return f"nc::linalg::svd({', '.join(args)})"
        elif func in ["np.linalg.norm", "numpy.linalg.norm"]:
            return f"nc::linalg::norm({', '.join(args)})"
        # NumPy array methods
        elif func.endswith(".reshape"):
            obj = func.replace(".reshape", "")
            return f"{obj}.reshape({', '.join(args)})"
        elif func.endswith(".transpose"):
            obj = func.replace(".transpose", "")
            return f"{obj}.transpose()"
        # Multiprocessing support
        elif func == "Process":
            # Process(target=func, args=(a, b)) → std::thread(func, a, b)
            # Need to extract keyword arguments
            target_func = None
            thread_args = []
            for i, keyword in enumerate(node.keywords):
                if keyword.arg == "target":
                    target_func = self.visit(keyword.value)
                elif keyword.arg == "args":
                    # args is a tuple, extract elements
                    if isinstance(keyword.value, ast.Tuple):
                        thread_args = [self.visit(elt) for elt in keyword.value.elts]
            if target_func:
                return f"std::thread({target_func}, {', '.join(thread_args)})"
            return "std::thread()"
        elif func == "Pool":
            # Pool(n) → We'll use a placeholder, actual pool map will be handled separately
            # For now, just note the pool size
            return f"/* Pool with {args[0] if args else '4'} workers */"
        elif func == "Lock":
            return "std::mutex()"
        # Pool methods
        elif func.endswith(".start"):
            # thread.start() → Not needed in C++, thread starts automatically
            obj = func.replace(".start", "")
            return f"/* {obj} starts automatically */"
        elif func.endswith(".join"):
            # thread.join() → thread.join()
            obj = func.replace(".join", "")
            return f"{obj}.join()"
        # File operations
        elif func.endswith(".read"):
            # file.read() → read entire file into string
            obj = func.replace(".read", "")
            self.headers.add("<sstream>")
            self.headers.add("<iterator>")
            return f"std::string((std::istreambuf_iterator<char>({obj})), std::istreambuf_iterator<char>())"
        elif func.endswith(".readline"):
            # file.readline() → read single line
            obj = func.replace(".readline", "")
            return f"[&](){{ std::string _line; std::getline({obj}, _line); return _line; }}()"
        elif func.endswith(".readlines"):
            # file.readlines() → read all lines into vector
            obj = func.replace(".readlines", "")
            self.headers.add("<vector>")
            return f"[&](){{ std::vector<std::string> _lines; std::string _line; while(std::getline({obj}, _line)) _lines.push_back(_line); return _lines; }}()"
        elif func.endswith(".write"):
            # file.write(content) → write to file
            obj = func.replace(".write", "")
            return f"{obj} << {args[0]}"
        return f"{func}({', '.join(args)})"

    def visit_Attribute(self, node):
        value = self.visit(node.value)
        # Handle self.attribute -> just attribute (or this->attribute in C++)
        if value == "self":
            return node.attr
        # Handle NumPy array attributes that are properties in Python but methods in NumCpp
        elif node.attr == "shape":
            return f"{value}.shape()"
        elif node.attr == "size":
            return f"{value}.size()"
        elif node.attr == "T":
            return f"{value}.transpose()"
        return f"{value}.{node.attr}"

    def visit_Expr(self, node):
        # Expression statement (e.g., standalone function call like print())
        value = self.visit(node.value)
        self.code.append(f"{self.indent()}{value};")

    def visit_Return(self, node):
        # Check if we're returning a tuple (multiple values)
        if isinstance(node.value, ast.Tuple):
            self.headers.add("<tuple>")
            elements = [self.visit(elt) for elt in node.value.elts]
            value = f"std::make_tuple({', '.join(elements)})"
        else:
            value = self.visit(node.value)

        # Use co_return in async functions
        if self.current_function_is_async:
            self.code.append(f"{self.indent()}co_return {value};")
        else:
            self.code.append(f"{self.indent()}return {value};")

    def visit_Await(self, node):
        # await expr → co_await expr
        value = self.visit(node.value)
        return f"co_await {value}"

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        # Handle power operator specially
        if isinstance(node.op, ast.Pow):
            self.headers.add("<cmath>")
            return f"std::pow({left}, {right})"

        op = self.visit(node.op)
        return f"{left} {op} {right}"

    def visit_UnaryOp(self, node):
        op = self.visit(node.op)
        operand = self.visit(node.operand)
        # Add parentheses for complex expressions to preserve precedence
        if isinstance(node.operand, (ast.BinOp, ast.Compare, ast.BoolOp)):
            return f"{op}({operand})"
        return f"{op}{operand}"

    def visit_UAdd(self, node):
        return "+"

    def visit_USub(self, node):
        return "-"

    def visit_Not(self, node):
        return "!"

    def visit_Add(self, node):
        return "+"

    def visit_Sub(self, node):
        return "-"

    def visit_Mult(self, node):
        return "*"

    def visit_Div(self, node):
        return "/"

    def visit_Mod(self, node):
        return "%"

    def visit_Pow(self, node):
        # Power operator ** → std::pow
        # This is handled differently - we need to modify visit_BinOp
        return "**"  # Placeholder, actual conversion happens in visit_BinOp

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

    def visit_Try(self, node):
        # Try/except/finally → C++ try/catch
        self.headers.add("<stdexcept>")

        # Try block
        self.code.append(f"{self.indent()}try {{")
        self.indentation_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation_level -= 1
        self.code.append(f"{self.indent()}}}")

        # Exception handlers (except clauses)
        for handler in node.handlers:
            if handler.type:
                # Specific exception type
                exc_type = self.visit(handler.type)
                # Map Python exception types to C++ exception types
                cpp_exc_type = self._map_exception_type(exc_type)

                if handler.name:
                    # except ExceptionType as variable:
                    self.code.append(f"{self.indent()}catch (const {cpp_exc_type}& {handler.name}) {{")
                else:
                    # except ExceptionType:
                    self.code.append(f"{self.indent()}catch (const {cpp_exc_type}&) {{")
            else:
                # Catch-all: except:
                self.code.append(f"{self.indent()}catch (...) {{")

            self.indentation_level += 1
            for stmt in handler.body:
                self.visit(stmt)
            self.indentation_level -= 1
            self.code.append(f"{self.indent()}}}")

        # Finally block - execute after all catch blocks
        if node.finalbody:
            # Note: C++ doesn't have finally, but we can approximate by adding code after catch blocks
            # This won't execute if there's an uncaught exception, but that's a limitation
            for stmt in node.finalbody:
                self.visit(stmt)

    def _map_exception_type(self, python_type):
        """Map Python exception types to C++ exception types"""
        exception_map = {
            "Exception": "std::exception",
            "ValueError": "std::invalid_argument",
            "TypeError": "std::invalid_argument",
            "RuntimeError": "std::runtime_error",
            "KeyError": "std::out_of_range",
            "IndexError": "std::out_of_range",
            "ZeroDivisionError": "std::overflow_error",
            "FileNotFoundError": "std::runtime_error",
            "IOError": "std::runtime_error",
        }
        return exception_map.get(python_type, "std::exception")

    def visit_Raise(self, node):
        # Raise exception
        self.headers.add("<stdexcept>")
        if node.exc:
            exc_type = None
            exc_msg = None

            if isinstance(node.exc, ast.Call):
                # raise ExceptionType("message")
                exc_type = self.visit(node.exc.func)
                if node.exc.args:
                    exc_msg = self.visit(node.exc.args[0])
            elif isinstance(node.exc, ast.Name):
                # raise exception_variable
                exc_type = self.visit(node.exc)

            cpp_exc_type = self._map_exception_type(exc_type) if exc_type else "std::runtime_error"

            if exc_msg:
                self.code.append(f"{self.indent()}throw {cpp_exc_type}({exc_msg});")
            else:
                self.code.append(f'{self.indent()}throw {cpp_exc_type}("Exception");')
        else:
            # re-raise current exception
            self.code.append(f"{self.indent()}throw;")

    def visit_With(self, node):
        # Context manager: with open(...) as f:
        self.headers.add("<fstream>")
        self.headers.add("<string>")

        # Process the first context manager (typically open())
        item = node.items[0]
        context_expr = item.context_expr

        # Check if this is a file open() call
        if isinstance(context_expr, ast.Call) and isinstance(context_expr.func, ast.Name) and context_expr.func.id == "open":
            # Extract filename and mode
            filename = self.visit(context_expr.args[0]) if context_expr.args else '""'
            mode = "r"  # default mode

            # Check for mode in args or keywords
            if len(context_expr.args) > 1:
                mode_node = context_expr.args[1]
                if isinstance(mode_node, ast.Constant):
                    mode = mode_node.value

            # Determine C++ file stream type based on mode
            if "w" in mode or "a" in mode:
                stream_type = "std::ofstream"
                stream_mode = "std::ios::out"
                if "a" in mode:
                    stream_mode += " | std::ios::app"
            else:  # read mode
                stream_type = "std::ifstream"
                stream_mode = "std::ios::in"

            # Get the variable name
            var_name = self.visit(item.optional_vars) if item.optional_vars else "_file"

            # Generate file stream opening
            self.code.append(f"{self.indent()}{{")  # Block scope for RAII
            self.indentation_level += 1
            if "w" in mode or "a" in mode:
                self.code.append(f"{self.indent()}{stream_type} {var_name}({filename}, {stream_mode});")
            else:
                self.code.append(f"{self.indent()}{stream_type} {var_name}({filename});")

            # Process the body
            for stmt in node.body:
                self.visit(stmt)

            self.indentation_level -= 1
            self.code.append(f"{self.indent()}}}  // {var_name} closes automatically")
        else:
            # Generic context manager (not fully supported)
            self.code.append(f"{self.indent()}// Unsupported context manager")
            for stmt in node.body:
                self.visit(stmt)

    def visit_Compare(self, node):
        left = self.visit(node.left)
        op = self.visit(node.ops[0])
        right = self.visit(node.comparators[0])
        return f"{left} {op} {right}"

    def visit_BoolOp(self, node):
        op = self.visit(node.op)
        values = [self.visit(value) for value in node.values]
        return f" {op} ".join(values)

    def visit_And(self, node):
        return "&&"

    def visit_Or(self, node):
        return "||"

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
        # Check if this is multi-dimensional indexing (NumPy array)
        if isinstance(node.slice, ast.Tuple):
            # Multi-dimensional indexing: arr[i,j] → arr(i,j) for NumCpp
            indices = [self.visit(dim) for dim in node.slice.elts]
            return f"{value}({', '.join(indices)})"
        else:
            slice = self.visit(node.slice)
            if value == "list":
                self.headers.add("<vector>")
                return f"std::vector<{slice}>"
            return f"{value}[{slice}]"

    def visit_Tuple(self, node):
        # For tuple literals like (1, 2, 3)
        elements = [self.visit(elt) for elt in node.elts]
        return f"{{{', '.join(elements)}}}"

    def visit_List(self, node):
        # For list literals like [1, 2, 3]
        elements = [self.visit(elt) for elt in node.elts]
        return f"{{{', '.join(elements)}}}"

    def visit_Dict(self, node):
        # For dictionary literals like {"a": 1, "b": 2}
        # Use std::map or initializer list
        self.headers.add("<map>")
        pairs = []
        for key, value in zip(node.keys, node.values):
            k = self.visit(key)
            v = self.visit(value)
            pairs.append(f"{{{k}, {v}}}")
        return f"{{{', '.join(pairs)}}}"

    def visit_ListComp(self, node):
        # List comprehension: [expr for var in iterable if condition]
        # Generate as immediately-invoked lambda expression (IIFE)
        self.headers.add("<vector>")

        # Build the comprehension as an IIFE
        lines = []
        lines.append("[]() {")
        lines.append("    std::vector<int> _result;")

        # Handle generators (for loops)
        for gen in node.generators:
            target = self.visit(gen.target)
            iter_expr = self.visit(gen.iter)
            lines.append(f"    for (auto {target} : {iter_expr}) {{")

            # Handle filters (if conditions)
            for if_clause in gen.ifs:
                condition = self.visit(if_clause)
                lines.append(f"        if ({condition}) {{")

        # Generate the element expression
        element = self.visit(node.elt)
        indent = "    " + "    " * len(node.generators) + "    " * sum(len(g.ifs) for g in node.generators)
        lines.append(f"{indent}_result.push_back({element});")

        # Close all the blocks
        for gen in reversed(node.generators):
            for _ in gen.ifs:
                lines.append("        }")
            lines.append("    }")

        lines.append("    return _result;")
        lines.append("}()")

        return "\n".join(lines)

    def visit_For(self, node):
        # Check if this is dictionary iteration (.items(), .keys(), .values())
        if isinstance(node.iter, ast.Call):
            func = node.iter.func
            if isinstance(func, ast.Attribute):
                dict_obj = self.visit(func.value)
                method = func.attr

                if method == "items":
                    # for key, value in dict.items() → for (auto& [key, value] : dict)
                    if isinstance(node.target, ast.Tuple):
                        # Structured binding (C++17)
                        vars = [self.visit(elt) for elt in node.target.elts]
                        self.code.append(f"{self.indent()}for (auto& [{', '.join(vars)}] : {dict_obj}) {{")
                    else:
                        # Single variable for pair
                        target = self.visit(node.target)
                        self.code.append(f"{self.indent()}for (auto& {target} : {dict_obj}) {{")
                elif method == "keys":
                    # for key in dict.keys() → for (auto& pair : dict) { auto key = pair.first;
                    target = self.visit(node.target)
                    self.code.append(f"{self.indent()}for (auto& _pair : {dict_obj}) {{")
                    self.indentation_level += 1
                    self.code.append(f"{self.indent()}auto {target} = _pair.first;")
                    self.indentation_level -= 1
                elif method == "values":
                    # for value in dict.values() → for (auto& pair : dict) { auto value = pair.second;
                    target = self.visit(node.target)
                    self.code.append(f"{self.indent()}for (auto& _pair : {dict_obj}) {{")
                    self.indentation_level += 1
                    self.code.append(f"{self.indent()}auto {target} = _pair.second;")
                    self.indentation_level -= 1
                else:
                    # Regular iteration
                    target = self.visit(node.target)
                    iter_name = self.visit(node.iter)
                    self.code.append(f"{self.indent()}for (auto {target} : {iter_name}) {{")

                self.indentation_level += 1
                for stmt in node.body:
                    self.visit(stmt)
                self.indentation_level -= 1
                self.code.append(f"{self.indent()}}}")
                return

        # Regular for loop
        target = self.visit(node.target)
        iter_name = self.visit(node.iter)

        # Try to infer the loop variable type from the iterator
        loop_var_type = "auto"
        if iter_name in self.variable_types:
            iter_type = self.variable_types[iter_name]
            # Extract element type from std::vector<T>
            if iter_type.startswith("std::vector<") and iter_type.endswith(">"):
                loop_var_type = iter_type[12:-1]  # Extract T from std::vector<T>

        self.code.append(f"{self.indent()}for ({loop_var_type} {target} : {iter_name}) {{")
        self.indentation_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation_level -= 1
        self.code.append(f"{self.indent()}}}")

    def visit_While(self, node):
        test = self.visit(node.test)
        self.code.append(f"{self.indent()}while ({test}) {{")
        self.indentation_level += 1
        for stmt in node.body:
            self.visit(stmt)
        self.indentation_level -= 1
        self.code.append(f"{self.indent()}}}")

    def visit_Break(self, node):
        self.code.append(f"{self.indent()}break;")

    def visit_Continue(self, node):
        self.code.append(f"{self.indent()}continue;")

    def visit_Lambda(self, node):
        # Lambda functions: lambda x, y: x + y → [](auto x, auto y) { return x + y; }
        # Use auto for parameters since Python lambdas don't have type annotations
        args = []
        for arg in node.args.args:
            # Check if we have type information for this parameter
            param_name = arg.arg
            if param_name in self.variable_types:
                param_type = self.variable_types[param_name]
            else:
                param_type = "auto"
            args.append(f"{param_type} {param_name}")

        args_str = ", ".join(args)
        body = self.visit(node.body)

        # For simple expressions, create a single-line lambda
        return f"[]({args_str}) {{ return {body}; }}"

    def visit_AugAssign(self, node):
        target = self.visit(node.target)
        op = self.visit(node.op)
        value = self.visit(node.value)
        self.code.append(f"{self.indent()}{target} {op}= {value};")

    def generate(self, node):
        self.visit(node)
        # If requests.hpp is used, remove nlohmann/json.hpp since it's already included
        if '"requests.hpp"' in self.headers and '"nlohmann/json.hpp"' in self.headers:
            self.headers.remove('"nlohmann/json.hpp"')
        sorted_headers = sorted(list(self.headers))
        header_str = "\n".join([f"#include {h}" for h in sorted_headers])
        if header_str:
            return f"{header_str}\n\n" + "\n".join(self.code)
        return "\n".join(self.code)


def generate_cpp(ast_tree):
    generator = CppGenerator()
    return generator.generate(ast_tree)