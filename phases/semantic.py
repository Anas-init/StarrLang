from .syntax import (
    Program, Declaration, Assignment, Print, Identifier, 
    StringLiteral, IntLiteral, ArrayLiteral, SliceExpr, ForEachLoop,
    WhileLoop, BinaryOp, ArrayAccess, FunctionCall
)


class SemanticAnalysis():

    def __init__(self):
        self.symbol_table = {}
        self.builtin_functions = {
            'length': 'function',
            'size': 'function'
        }

    def analyze(self, node):
        method_name = f"analyze_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_analyze)
        return method(node)

    def generic_analyze(self, node):
        raise Exception(f"No analyze_{type(node).__name__} method defined")

    def analyze_Program(self, node):
        for stmt in node.statements:
            self.analyze(stmt)

    def analyze_Declaration(self, node):
        if node.name in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{node.name}' already declared")
        
        expr_type = self.analyze(node.expression)
        
        if node.typename not in ("string", "int", "array"):
            raise Exception(f"Semantic Error: Invalid type '{node.typename}'")
        
        if node.typename != expr_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to {node.typename}")
        
        self.symbol_table[node.name] = node.typename

    def analyze_Assignment(self, node):
        if node.name not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{node.name}' not declared")
        var_type = self.symbol_table[node.name]
        expr_type = self.analyze(node.expression)

        if isinstance(node.expression, SliceExpr):
            raise Exception(f"Semantic Error: Cannot assign slice to variable '{node.name}'")

        if var_type != expr_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to {var_type}")

    def analyze_Print(self, node):
        printable_type = self.analyze(node.printable)
        return printable_type

    def analyze_Identifier(self, node):
        if node.name not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{node.name}' not declared")
        return self.symbol_table[node.name]

    def analyze_StringLiteral(self, node):
        return "string"

    def analyze_IntLiteral(self, node):
        return "int"

    def analyze_ArrayLiteral(self, node):
        if len(node.elements) == 0:
            return "array"
        
        for elem in node.elements:
            elem_type = self.analyze(elem)
            if elem_type != "string":
                raise Exception("Type Error: Arrays can only contain strings")
        return "array"

    def analyze_SliceExpr(self, node):
        if node.name not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{node.name}' not declared")
        var_type = self.symbol_table[node.name]
        if var_type not in ("string", "array"):
            raise Exception(f"Semantic Error: Cannot slice type '{var_type}'")
        
        start_type = self.analyze(node.start)
        end_type = self.analyze(node.end)
        
        if start_type != "int":
            raise Exception(f"Type Error: Slice start index must be int, got {start_type}")
        if end_type != "int":
            raise Exception(f"Type Error: Slice end index must be int, got {end_type}")
        
        if isinstance(node.start, IntLiteral) and isinstance(node.end, IntLiteral):
            if node.start.value < 0 or node.end.value < 0:
                raise Exception(f"Semantic Error: Slice indices must be non-negative")
            if node.start.value > node.end.value:
                raise Exception(f"Semantic Error: Slice start index > end index")
        
        return var_type

    def analyze_ForEachLoop(self, node):
        if node.iterable not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{node.iterable}' not declared")
        iter_type = self.symbol_table[node.iterable]
        if iter_type not in ("string", "array"):
            raise Exception(f"Semantic Error: Cannot iterate over type '{iter_type}'")
        if node.var in self.symbol_table:
            raise Exception(f"Semantic Error: Loop variable '{node.var}' already declared")
        
        self.symbol_table[node.var] = "string"

        for stmt in node.body:
            self.analyze(stmt)
        
        self.symbol_table.pop(node.var)

    def analyze_WhileLoop(self, node):
        condition_type = self.analyze(node.condition)
        
        if condition_type not in ("int", "boolean"):
            raise Exception(f"Type Error: While condition must be boolean or int, got {condition_type}")
        
        for stmt in node.body:
            self.analyze(stmt)

    def analyze_BinaryOp(self, node):
        left_type = self.analyze(node.left)
        right_type = self.analyze(node.right)
        
        if node.operator == '+':
            if left_type == "string" and right_type == "string":
                return "string"
            elif left_type == "int" and right_type == "int":
                return "int"
            else:
                raise Exception(f"Type Error: Cannot add {left_type} and {right_type}")
        
        elif node.operator == '-':
            if left_type == "int" and right_type == "int":
                return "int"
            else:
                raise Exception(f"Type Error: Cannot subtract {left_type} and {right_type}")
        
        elif node.operator in ('*', '/'):
            if left_type == "int" and right_type == "int":
                return "int"
            else:
                raise Exception(f"Type Error: Cannot perform {node.operator} on {left_type} and {right_type}")
        
        elif node.operator in ('<', '>', '<=', '>='):
            if left_type == right_type and left_type in ("int", "string"):
                return "boolean"
            else:
                raise Exception(f"Type Error: Cannot compare {left_type} and {right_type}")
        
        elif node.operator in ('==', '!='):
            if left_type == right_type:
                return "boolean"
            else:
                raise Exception(f"Type Error: Cannot compare {left_type} and {right_type}")
        
        return left_type

    def analyze_ArrayAccess(self, node):
        if node.name not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{node.name}' not declared")
        
        var_type = self.symbol_table[node.name]
        index_type = self.analyze(node.index)
        
        if index_type != "int":
            raise Exception(f"Type Error: Array/string index must be int, got {index_type}")
        
        if var_type == "array":
            return "string"
        elif var_type == "string":
            return "string"
        else:
            raise Exception(f"Semantic Error: Cannot index type '{var_type}'")

    def analyze_FunctionCall(self, node):
        if node.name not in self.builtin_functions:
            raise Exception(f"Semantic Error: Unknown function '{node.name}'")
        
        if node.name == "length":
            if len(node.arguments) != 1:
                raise Exception(f"Semantic Error: length() takes exactly 1 argument")
            arg_type = self.analyze(node.arguments[0])
            if arg_type != "string":
                raise Exception(f"Type Error: length() requires string argument, got {arg_type}")
            return "int"
        
        elif node.name == "size":
            if len(node.arguments) != 1:
                raise Exception(f"Semantic Error: size() takes exactly 1 argument")
            arg_type = self.analyze(node.arguments[0])
            if arg_type != "array":
                raise Exception(f"Type Error: size() requires array argument, got {arg_type}")
            return "int"
        
        return "int"