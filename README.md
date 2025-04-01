# Autonomous AI Code Debugger

## Overview
This project implements an autonomous AI code debugger that can analyze Python code to identify errors, suggest optimizations, and recommend improvements without human intervention. The debugger uses Python's Abstract Syntax Tree (AST) to parse and analyze code, detecting common issues such as syntax errors, undefined variables, unused variables, potential division by zero, inefficient loops, and redundant code.

## Features
- **Syntax Error Detection**: Identifies and reports syntax errors, indentation issues, and other parsing problems.
- **Undefined Variable Detection**: Locates uses of variables that haven't been defined, excluding built-ins and imports.
- **Unused Variable Detection**: Finds variables that are defined but never used.
- **Division by Zero Prevention**: Detects potential division by zero operations.
- **Inefficient Loop Detection**: Identifies loops that could be optimized with more efficient constructs.
- **Redundant Code Elimination**: Spots unnecessary operations like self-assignment or adding zero.
- **Type Hint Suggestions**: Recommends adding type hints to improve code readability and maintainability.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-code-debugger.git
cd ai-code-debugger

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage
```python
from main import CodeDebugger

# Create a debugger instance with your code
code = """
def calculate_sum(a, b):
    unused_var = 42
    result = a + b
    print(x)  # Undefined variable
    return result
"""

debugger = CodeDebugger(code)
results = debugger.analyze()

# Print results
print("Errors:")
for error in results["errors"]:
    print(f"- {error}")

print("\nOptimizations:")
for opt in results["optimizations"]:
    print(f"- {opt}")

print("\nSuggestions:")
for suggestion in results["suggestions"]:
    print(f"- {suggestion}")
```

### Command Line Usage
The script can also be run directly to debug the built-in samples:

```bash
python main.py
```

## How It Works

The debugger works by:

1. **Parsing**: Converting the code string into an Abstract Syntax Tree (AST)
2. **Analysis**: Walking through the AST to identify various issues
3. **Reporting**: Generating a detailed report of errors, optimizations, and suggestions

## Analysis Types

### Error Detection
- **Syntax Errors**: Basic syntax issues that prevent code from running
- **Undefined Variables**: Variables used before being defined
- **Unused Variables**: Variables defined but never used
- **Division by Zero**: Potential runtime errors from division by zero

### Optimization Suggestions
- **Inefficient Loops**: Loops that could be replaced with more efficient constructs
- **List Operations**: Identifying when list comprehensions would be more efficient

### Code Improvement Suggestions
- **Type Hints**: Suggestions for adding type annotations
- **Redundant Operations**: Identifying and removing unnecessary code

## Extending the Debugger

To add new analysis capabilities:
1. Create a new method in the `CodeDebugger` class
2. Implement the analysis logic using AST node inspection
3. Add appropriate results to `self.errors`, `self.optimizations`, or `self.suggestions`
4. Call your method from the `analyze()` method

## Limitations
- The debugger only analyzes static code and cannot detect runtime-specific issues
- Type inference is basic and may not accurately determine complex types
- The analyzer doesn't track variable modifications through the code flow
- Only checks for a limited set of predefined patterns

## Future Improvements
- Add data flow analysis to track variable values
- Implement more complex pattern recognition for code smells
- Add automatic code fixing capabilities
- Extend to support other programming languages
- Add integration with popular IDEs and code editors

## License
[MIT License](LICENSE)

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
