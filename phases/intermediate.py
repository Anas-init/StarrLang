from .syntax import (
    Program, Declaration, Assignment, Print, Identifier, 
    StringLiteral, ArrayLiteral, SliceExpr, ForEachLoop
)


class IntermediateCode():

    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        """Generate a new temporary variable"""
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp

    def new_label(self):
        """Generate a new label"""
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    def emit(self, instruction):
        """Add an instruction to the intermediate code"""
        self.code.append(instruction)

    def generate(self, node):
        """Generate intermediate code for a node"""
        method_name = f"generate_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_generate)
        return method(node)

    def generic_generate(self, node):
        raise Exception(f"No generate_{type(node).__name__} method defined")

    def generate_Program(self, node):
        """Generate code for the entire program"""
        for stmt in node.statements:
            self.generate(stmt)
        return self.code

    def generate_Declaration(self, node):
        """Generate code for variable declaration
        Format: typename name = expression
        """
        expr_result = self.generate(node.expression)
        
        self.emit(f"{node.typename} {node.name} = {expr_result}")

    def generate_Assignment(self, node):
        """Generate code for assignment
        Format: name = expression
        """
        expr_result = self.generate(node.expression)
        
        self.emit(f"{node.name} = {expr_result}")

    def generate_Print(self, node):
        """Generate code for print statement
        Format: print expression
        """
        printable_result = self.generate(node.printable)
        
        self.emit(f"print {printable_result}")

    def generate_Identifier(self, node):
        """Return the identifier name"""
        return node.name

    def generate_StringLiteral(self, node):
        """Return the string literal value"""
        return node.value

    def generate_ArrayLiteral(self, node):
        """Generate code for array literal
        Format: {elem1, elem2, ...}
        """
        elements = []
        for elem in node.elements:
            elem_result = self.generate(elem)
            elements.append(elem_result)
        
        return "{" + ", ".join(elements) + "}"

    def generate_SliceExpr(self, node):
        """Generate code for slice expression
        Format: name[start:end]
        """
        return f"{node.name}[{node.start}:{node.end}]"

    def generate_ForEachLoop(self, node):
        """Generate code for for-each loop
        Three-address code with labels:
        
        L_start:
            if loop_var has_next iterable goto L_body
            goto L_end
        L_body:
            loop_var = next(iterable)
            [body statements]
            goto L_start
        L_end:
        """
        label_start = self.new_label()
        label_body = self.new_label()
        label_end = self.new_label()
        
        iter_temp = self.new_temp()
        
        self.emit(f"{iter_temp} = iterator({node.iterable})")
        
        self.emit(f"{label_start}:")
        
        self.emit(f"if has_next({iter_temp}) goto {label_body}")
        self.emit(f"goto {label_end}")
        
        self.emit(f"{label_body}:")
        
        self.emit(f"string {node.var} = next({iter_temp})")
        
        for stmt in node.body:
            self.generate(stmt)
        
        self.emit(f"goto {label_start}")
        
        self.emit(f"{label_end}:")

    def print_code(self):
        """Print the generated intermediate code"""
        print("\n=== Intermediate Code ===")
        for i, instruction in enumerate(self.code):
            print(f"{i+1:3}. {instruction}")
        print("=" * 25)

    def get_code(self):
        """Return the list of intermediate code instructions"""
        return self.code