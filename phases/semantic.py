from .syntax import (
    Program, Declaration, Assignment, Print, Identifier, 
    StringLiteral, ArrayLiteral, SliceExpr, ForEachLoop
)


class SemanticAnalysis():

    def __init__(self):
        
        self.symbol_table = {}

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
        
        # Analyze expression type
        expr_type = self.analyze(node.expression)
        # Check if type matches declaration
        if node.typename != expr_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to {node.typename}")
        # Add to symbol table
        self.symbol_table[node.name] = node.typename

    # ---------------- Assignment ----------------
    def analyze_Assignment(self, node):
        if node.name not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{node.name}' not declared")
        var_type = self.symbol_table[node.name]
        expr_type = self.analyze(node.expression)

        # Slice cannot be assigned
        if isinstance(node.expression, SliceExpr):
            raise Exception(f"Semantic Error: Cannot assign slice to variable '{node.name}'")

        if var_type != expr_type:
            raise Exception(f"Type Error: Cannot assign {expr_type} to {var_type}")

    # ---------------- Print ----------------
    def analyze_Print(self, node):
        printable_type = self.analyze(node.printable)
        return printable_type  # Not strictly needed, but useful

    # ---------------- Identifier ----------------
    def analyze_Identifier(self, node):
        if node.name not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{node.name}' not declared")
        return self.symbol_table[node.name]

    # ---------------- StringLiteral ----------------
    def analyze_StringLiteral(self, node):
        return "string"

    # ---------------- ArrayLiteral ----------------
    def analyze_ArrayLiteral(self, node):
        # All elements should have same type (string only for simplicity)
        for elem in node.elements:
            elem_type = self.analyze(elem)
            if elem_type != "string":
                raise Exception("Type Error: Arrays can only contain strings")
        return "array"

    # ---------------- SliceExpr ----------------
    def analyze_SliceExpr(self, node):
        # Must exist in symbol table
        if node.name not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{node.name}' not declared")
        var_type = self.symbol_table[node.name]
        if var_type not in ("string", "array"):
            raise Exception(f"Semantic Error: Cannot slice type '{var_type}'")
        # Check bounds
        if node.start < 0 or node.end < 0:
            raise Exception(f"Semantic Error: Slice indices must be non-negative")
        if node.start > node.end:
            raise Exception(f"Semantic Error: Slice start index > end index")
        return var_type  # Type of slice is same as variable type

    # ---------------- ForEachLoop ----------------
    def analyze_ForEachLoop(self, node):
        if node.iterable not in self.symbol_table:
            raise Exception(f"Semantic Error: Variable '{node.iterable}' not declared")
        iter_type = self.symbol_table[node.iterable]
        if iter_type not in ("string", "array"):
            raise Exception(f"Semantic Error: Cannot iterate over type '{iter_type}'")
        if node.var in self.symbol_table:
            raise Exception(f"Semantic Error: Loop variable '{node.var}' already declared")
        self.symbol_table[node.var] = "string" if iter_type=="string" else "string" # elements are strings

        for stmt in node.body:
            self.analyze(stmt)
        self.symbol_table.pop(node.var)
