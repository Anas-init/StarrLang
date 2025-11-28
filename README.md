# StarrLang

A complete compiler implementation for a custom mini programming language focused on string and array manipulation. The language features C++-like syntax with support for slicing operations, foreach loops, and type checking.

## Overview

This project implements a full compiler pipeline from lexical analysis through code generation and interpretation. The language is designed to be simple yet functional, with emphasis on string and array operations commonly used in text processing tasks.

## Language Features

- String and array data types
- Array and string slicing with inclusive indexing
- Foreach loops for iteration
- Type checking and semantic analysis
- C++ inspired syntax

### Syntax Examples

```cpp
// Array declaration and slicing
array names = {"Alice", "Bob", "Charlie"};
cout << names[0:2];

// String operations
string message = "Hello World";
cout << message[0:4];

// Foreach loop
for (item in names) {
    cout << item;
}
```

## Architecture

The compiler consists of seven distinct phases:

### 1. Lexical Analysis
Tokenizes the source code into a stream of tokens using regular expressions. Recognizes keywords, identifiers, literals, operators, and punctuation.

### 2. Syntax Analysis
Builds an Abstract Syntax Tree (AST) from the token stream using recursive descent parsing. Validates the grammatical structure of the program.

### 3. Semantic Analysis
Performs type checking and maintains a symbol table. Ensures variables are declared before use, types match in assignments, and enforces language constraints like slice-only-in-print rules.

### 4. Intermediate Code Generation
Translates the AST into three-address code format. Loops are converted to labeled instructions with explicit control flow.

### 5. Code Optimization
Applies several optimization techniques:
- Dead code elimination
- Copy propagation
- Redundant label removal
- Unreachable code elimination

### 6. Code Generation
Generates executable Python code from the optimized intermediate representation. The output is syntactically correct Python that can be run independently.

### 7. Interpretation
Directly executes the intermediate code without generating an external file. Maintains runtime state and produces program output.

## Project Structure

```
mini-language-compiler/
├── gui.py                      # Graphical user interface
├── main.py                     # Command-line interface
├── clear_comments.py           # Utility script
├── phases/
│   ├── __init__.py
│   ├── lexical.py             # Lexical analyzer
│   ├── syntax.py              # Parser
│   ├── semantic.py            # Semantic analyzer
│   ├── intermediate.py        # IR generator
│   ├── optimizer.py           # Code optimizer
│   ├── codegen.py             # Python code generator
│   └── interpreter.py         # IR interpreter
└── README.md
```

## Installation

### Prerequisites

- Python 3.7 or higher
- tkinter (usually included with Python)

### Setup

Clone the repository:

```bash
git clone https://github.com/yourusername/mini-language-compiler.git
cd mini-language-compiler
```

No additional dependencies are required. The project uses only Python standard library modules.

## Usage

### Graphical Interface

Run the GUI application:

```bash
python gui.py
```

The interface provides:
- Code editor with syntax input
- Tabbed output for each compilation phase
- Sample programs via dropdown menu
- Real-time compilation and execution

### Command Line Interface

Run the command-line version:

```bash
python main.py
```

Select from predefined test cases or modify the code directly in the script.

### Programmatic Usage

```python
from phases.lexical import LexicalAnalysis
from phases.syntax import SyntaxAnalysis
from phases.semantic import SemanticAnalysis
from phases.intermediate import IntermediateCode
from phases.optimizer import Optimizer
from phases.codegen import CodeGenerator
from phases.interpreter import Interpreter

# Define token specifications
tokens = [...]

# Compile and execute
code = 'array arr = {"A", "B", "C"}; cout << arr[0:1];'

lex = LexicalAnalysis(tokens)
syn = SyntaxAnalysis(lex.lexer(code))
syntax_tree = syn.parse_program()

sem = SemanticAnalysis()
sem.analyze(syntax_tree)

ic = IntermediateCode()
ic.generate(syntax_tree)

optimizer = Optimizer(ic.get_code())
optimized = optimizer.optimize()

interpreter = Interpreter(optimized)
interpreter.execute()
```

## Language Specification

### Data Types

- `string`: Character sequences enclosed in double quotes
- `array`: Ordered collections of strings

### Operators

- `=`: Assignment
- `<<`: Output operator (used with cout)
- `[start:end]`: Slice operator (inclusive range)

### Keywords

- `string`, `array`: Type declarations
- `for`, `in`: Loop constructs
- `cout`: Output statement

### Grammar

```
program        → statement*
statement      → declaration | assignment | print | for_loop
declaration    → type IDENTIFIER '=' expression ';'
assignment     → IDENTIFIER '=' expression ';'
print          → 'cout' '<<' printable ';'
printable      → IDENTIFIER | STRING_LITERAL | slice
slice          → IDENTIFIER '[' NUMBER ':' NUMBER ']'
for_loop       → 'for' '(' IDENTIFIER 'in' IDENTIFIER ')' '{' statement* '}'
expression     → STRING_LITERAL | IDENTIFIER | array_literal
array_literal  → '{' expression (',' expression)* '}'
```

## Optimization Techniques

The optimizer implements several standard compiler optimizations:

**Dead Code Elimination**: Removes variable declarations and assignments that are never used in the program.

**Copy Propagation**: Replaces variables that are simple copies of other variables with the original variable reference.

**Redundant Label Removal**: Eliminates labels that are never targeted by jump instructions.

**Unreachable Code Elimination**: Removes code that can never be executed due to control flow.

## Testing

The project includes several test cases covering different language features:

1. Basic array slicing
2. String slicing
3. Foreach loops
4. Complex programs with optimization opportunities
5. Dead code elimination scenarios

Run tests using either the GUI or command-line interface.

## Utility Scripts

### Comment Cleaner

Remove comments from all Python files in the project:

```bash
python clear_comments.py
```

Creates automatic backups before modifying files. Preserves docstrings and string literals.

## Technical Details

### Intermediate Representation

The compiler generates three-address code with the following instruction formats:

```
type name = value          # Declaration
name = value               # Assignment
print expression           # Output
tN = iterator(iterable)    # Iterator creation
if condition goto label    # Conditional jump
goto label                 # Unconditional jump
label:                     # Jump target
```

### Type System

The type system is simple but strict:
- Variables must be declared before use
- Type mismatches in assignments are errors
- Arrays can only contain strings
- Slicing is restricted to print statements

### Error Handling

The compiler provides meaningful error messages for:
- Undeclared variables
- Type mismatches
- Invalid slice operations
- Syntax errors

## Limitations

- Only string and array types are supported
- No arithmetic operations
- No function definitions
- Limited control flow (only foreach loops)
- Arrays are restricted to string elements
- No nested data structures

## Future Enhancements

Potential improvements for the language and compiler:

- Add numeric types and arithmetic operations
- Implement while loops and conditional statements
- Support function definitions and calls
- Add more optimization passes
- Implement register allocation
- Generate assembly or bytecode instead of Python
- Add standard library functions
- Support nested arrays and complex data structures

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Add tests for new features
5. Ensure all phases work correctly
6. Submit a pull request

## License

This project is available under the MIT License. See LICENSE file for details.

## Authors

Developed as an educational compiler project demonstrating the complete compilation pipeline.

## Acknowledgments

This compiler implements standard techniques from compiler design literature, including concepts from the Dragon Book and other compiler construction resources.
