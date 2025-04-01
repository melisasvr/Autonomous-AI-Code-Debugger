import ast
from typing import Any

class CodeDebugger:
    def __init__(self, code_string):
        """Initialize with the code to debug."""
        self.code = code_string.strip()
        self.tree = None
        self.errors = []
        self.optimizations = []
        self.suggestions = []

    def parse_code(self):
        """Parse the code into an AST and handle syntax errors."""
        try:
            self.tree = ast.parse(self.code, filename="<user_code>")
            return True
        except (SyntaxError, IndentationError, TabError) as e:
            self.errors.append(f"SyntaxError: {str(e)} at line {e.lineno}")
            return False
        except Exception as e:
            self.errors.append(f"Unexpected error during parsing: {str(e)}")
            return False

    def check_undefined_variables(self):
        """Find undefined variables, excluding built-ins and imports."""
        if not self.tree:
            return

        builtins = set(__import__("builtins").__dict__.keys()) | {"True", "False", "None"}
        defined_names = set()
        imported_names = set()

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imported_names.add(name.asname or name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    imported_names.add(name.asname or name.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined_names.add(node.id)
            elif isinstance(node, ast.FunctionDef):
                defined_names.add(node.name)
                for arg in node.args.args:
                    defined_names.add(arg.arg)

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if (node.id not in defined_names and 
                    node.id not in builtins and 
                    node.id not in imported_names):
                    self.errors.append(f"Undefined variable '{node.id}' used at line {node.lineno}. Fix: Define '{node.id}' before use.")

    def check_unused_variables(self):
        """Find variables defined but never used, excluding function names."""
        if not self.tree:
            return

        defined_names = {}
        used_names = set()
        function_names = set()

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                function_names.add(node.name)
                for arg in node.args.args:
                    defined_names[arg.arg] = arg.lineno
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined_names[node.id] = node.lineno
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)

        for name, lineno in defined_names.items():
            if name not in used_names and name not in function_names:
                self.errors.append(f"Unused variable '{name}' defined at line {lineno}.")

    def check_division_by_zero(self):
        """Detect potential division by zero."""
        if not self.tree:
            return

        for node in ast.walk(self.tree):
            if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                if isinstance(node.right, ast.Constant) and node.right.value == 0:
                    self.errors.append(f"Division by zero at line {node.lineno}. Fix: Avoid dividing by zero.")
                elif isinstance(node.right, ast.Name):
                    self.suggestions.append(f"Line {node.lineno}: Add check to ensure '{node.right.id}' is not zero before division.")

    def check_inefficient_loops(self):
        """Detect inefficient loops and suggest optimizations."""
        if not self.tree:
            return

        for node in ast.walk(self.tree):
            if isinstance(node, ast.For):
                if (isinstance(node.iter, ast.Call) and 
                    isinstance(node.iter.func, ast.Name) and 
                    node.iter.func.id == "range"):
                    is_simple_sum = all(
                        isinstance(n, ast.AugAssign) and isinstance(n.op, ast.Add)
                        for n in node.body
                    )
                    if is_simple_sum:
                        self.optimizations.append(
                            f"Line {node.lineno}: Replace loop with sum(range(...)) for efficiency."
                        )
                elif any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "append" 
                         for n in ast.walk(node)):
                    self.optimizations.append(
                        f"Line {node.lineno}: Consider using a list comprehension for efficiency if applicable."
                    )

    def check_redundant_code(self):
        """Detect simple redundant operations."""
        if not self.tree:
            return

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                    target = node.targets[0].id
                    if isinstance(node.value, ast.Name) and node.value.id == target:
                        self.errors.append(f"Redundant assignment '{target} = {target}' at line {node.lineno}. Fix: Remove this line.")
                    elif (isinstance(node.value, ast.BinOp) and 
                          isinstance(node.value.op, ast.Add) and 
                          isinstance(node.value.right, ast.Constant) and 
                          node.value.right.value == 0):
                        self.errors.append(f"Redundant operation '{target} = {target} + 0' at line {node.lineno}. Fix: Remove this line.")

    def suggest_type_hints(self):
        """Suggest adding type hints for functions."""
        if not self.tree:
            return

        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                return_type = "Any"
                for ret_node in ast.walk(node):
                    if isinstance(ret_node, ast.Return) and ret_node.value:
                        if isinstance(ret_node.value, ast.Constant):
                            if isinstance(ret_node.value.value, int):
                                return_type = "int"
                            elif isinstance(ret_node.value.value, float):
                                return_type = "float"
                            elif isinstance(ret_node.value.value, str):
                                return_type = "str"
                        elif isinstance(ret_node.value, ast.List):
                            return_type = "list"
                        break
                # Infer parameter types from usage
                param_types = {arg.arg: "Any" for arg in node.args.args}
                for body_node in ast.walk(node):
                    if isinstance(body_node, ast.BinOp):
                        if isinstance(body_node.op, (ast.Add, ast.Sub, ast.Mult)):
                            for arg in node.args.args:
                                if (isinstance(body_node.left, ast.Name) and body_node.left.id == arg.arg) or \
                                   (isinstance(body_node.right, ast.Name) and body_node.right.id == arg.arg):
                                    param_types[arg.arg] = "int"  # Default to int for arithmetic

                if not node.returns:
                    self.suggestions.append(f"Line {node.lineno}: Add type hint for return value of '{node.name}' (e.g., -> {return_type}).")
                for arg in node.args.args:
                    if not arg.annotation:
                        self.suggestions.append(f"Line {arg.lineno}: Add type hint for parameter '{arg.arg}' in '{node.name}' (e.g., {arg.arg}: {param_types[arg.arg]}).")

    def analyze(self):
        """Run all analysis steps and return results."""
        if not self.parse_code():
            return {"errors": self.errors, "optimizations": [], "suggestions": []}

        self.check_undefined_variables()
        self.check_unused_variables()
        self.check_division_by_zero()
        self.check_inefficient_loops()
        self.check_redundant_code()
        self.suggest_type_hints()

        return {"errors": self.errors, "optimizations": self.optimizations, "suggestions": self.suggestions}

def debug_code(code_string, sample_name):
    """Debug a single code sample and display results."""
    print(f"\n{'='*20} Debugging sample: {sample_name} {'='*20}")
    print("Code:")
    print(code_string.strip())
    print("-" * 50)

    debugger = CodeDebugger(code_string)
    results = debugger.analyze()

    if results["errors"]:
        print("Errors found:")
        for error in results["errors"]:
            print(f"  - {error}")
    else:
        print("No errors found.")

    if results["optimizations"]:
        print("\nOptimization suggestions:")
        for opt in results["optimizations"]:
            print(f"  - {opt}")
    else:
        print("\nNo optimization suggestions.")

    if results["suggestions"]:
        print("\nCode improvement suggestions:")
        for sug in results["suggestions"]:
            print(f"  - {sug}")
    else:
        print("\nNo code improvement suggestions.")

def debug_multiple_samples():
    """Debug a list of sample codes."""
    samples = [
        {
            "name": "Sample 1: Original Example",
            "code": """
def calculate_sum(a, b):
    unused_var = 42
    result = a + b
    print(x)  # Undefined variable
    for i in range(1000000):
        result += i  # Inefficient loop
    result = result  # Redundant
    risky = 10 / 0  # Division by zero
    return result
            """
        },
        {
            "name": "Sample 2: Simple Function",
            "code": """
def multiply(x, y):
    z = x * y
    return z
            """
        },
        {
            "name": "Sample 3: Syntax Error",
            "code": """
def broken_function(a)
    return a + 1
            """
        },
    ]

    for sample in samples:
        debug_code(sample["code"], sample["name"])

if __name__ == "__main__":
    debug_multiple_samples()