from .syntax import (
    Program, Declaration, Assignment, Print, Identifier, 
    StringLiteral, IntLiteral, ArrayLiteral, SliceExpr, ForEachLoop,
    WhileLoop, BinaryOp, ArrayAccess, FunctionCall
)


class IntermediateCode():

    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def new_temp(self):
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp

    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    def emit(self, instruction):
        self.code.append(instruction)

    def generate(self, node):
        method_name = f"generate_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_generate)
        return method(node)

    def generic_generate(self, node):
        raise Exception(f"No generate_{type(node).__name__} method defined")

    def generate_Program(self, node):
        for stmt in node.statements:
            self.generate(stmt)
        return self.code

    def generate_Declaration(self, node):
        expr_result = self.generate(node.expression)
        self.emit(f"{node.typename} {node.name} = {expr_result}")

    def generate_Assignment(self, node):
        expr_result = self.generate(node.expression)
        self.emit(f"{node.name} = {expr_result}")

    def generate_Print(self, node):
        printable_result = self.generate(node.printable)
        self.emit(f"print {printable_result}")

    def generate_Identifier(self, node):
        return node.name

    def generate_StringLiteral(self, node):
        return node.value

    def generate_IntLiteral(self, node):
        return str(node.value)

    def generate_ArrayLiteral(self, node):
        elements = []
        for elem in node.elements:
            elem_result = self.generate(elem)
            elements.append(elem_result)
        return "{" + ", ".join(elements) + "}"

    def generate_SliceExpr(self, node):
        start_result = self.generate(node.start)
        end_result = self.generate(node.end)
        return f"{node.name}[{start_result}:{end_result}]"

    def generate_ForEachLoop(self, node):
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

    def generate_WhileLoop(self, node):
        label_start = self.new_label()
        label_body = self.new_label()
        label_end = self.new_label()
        
        self.emit(f"{label_start}:")
        
        condition_temp = self.generate(node.condition)
        
        self.emit(f"if {condition_temp} goto {label_body}")
        self.emit(f"goto {label_end}")
        self.emit(f"{label_body}:")
        
        for stmt in node.body:
            self.generate(stmt)
        
        self.emit(f"goto {label_start}")
        self.emit(f"{label_end}:")

    def generate_BinaryOp(self, node):
        left_result = self.generate(node.left)
        right_result = self.generate(node.right)
        
        temp = self.new_temp()
        self.emit(f"{temp} = {left_result} {node.operator} {right_result}")
        return temp

    def generate_ArrayAccess(self, node):
        index_result = self.generate(node.index)
        return f"{node.name}[{index_result}]"

    def generate_FunctionCall(self, node):
        if node.name in ("length", "size"):
            arg_result = self.generate(node.arguments[0])
            temp = self.new_temp()
            self.emit(f"{temp} = {node.name}({arg_result})")
            return temp
        
        return "unknown"

    def print_code(self):
        print("\n=== Intermediate Code ===")
        for i, instruction in enumerate(self.code):
            print(f"{i+1:3}. {instruction}")
        print("=" * 25)

    def get_code(self):
        return self.code