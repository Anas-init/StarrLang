class CodeGenerator():

    def __init__(self, optimized_code):
        self.intermediate_code = optimized_code
        self.python_code = []
        self.indent_level = 0

    def generate(self):
        """Generate Python code from intermediate code"""
        print("\n=== Generating Python Code ===")
        
        self.emit("# Generated Python Code")
        self.emit("")
        
        i = 0
        while i < len(self.intermediate_code):
            instruction = self.intermediate_code[i].strip()
            
            if instruction.endswith(':'):
                self.handle_label(instruction, i)
            elif instruction.startswith('if '):
                pass
            elif instruction.startswith('goto '):
                pass
            elif instruction.startswith('print '):
                self.handle_print(instruction)
            elif '= iterator(' in instruction:
                i = self.handle_for_loop(i)
            elif '=' in instruction:
                self.handle_assignment(instruction)
            
            i += 1
        
        print("Python code generation complete!")
        print("=" * 30)
        return '\n'.join(self.python_code)

    def emit(self, code):
        """Add a line of Python code with proper indentation"""
        if code:
            self.python_code.append('    ' * self.indent_level + code)
        else:
            self.python_code.append('')

    def handle_assignment(self, instruction):
        """Convert assignment to Python"""
        parts = instruction.split('=', 1)
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        lhs_tokens = lhs.split()
        var_name = lhs_tokens[-1] if lhs_tokens else lhs
        
        python_rhs = self.convert_expression(rhs)
        
        self.emit(f"{var_name} = {python_rhs}")

    def handle_print(self, instruction):
        """Convert print statement to Python"""
        expr = instruction.split('print ', 1)[1].strip()
        
        if '[' in expr and ':' in expr:
            var_name = expr.split('[')[0]
            slice_part = expr.split('[')[1].split(']')[0]
            start, end = slice_part.split(':')
            start = int(start)
            end = int(end)
            
            self.emit(f"print({var_name}[{start}:{end+1}])")
        else:
            python_expr = self.convert_expression(expr)
            self.emit(f"print({python_expr})")

    def handle_label(self, instruction, index):
        """Handle label - usually part of loop structure"""
        label = instruction[:-1]
        self.emit(f"# {label}")

    def handle_for_loop(self, start_index):
        """Detect and convert for loop structure to Python for loop"""
        
        i = start_index
        iterator_line = self.intermediate_code[i].strip()
        
        iterable = iterator_line.split('iterator(')[1].split(')')[0]
        
        loop_var = None
        body_start = -1
        body_end = -1
        
        for j in range(i, len(self.intermediate_code)):
            line = self.intermediate_code[j].strip()
            if 'next(' in line and '=' in line:
                parts = line.split('=', 1)
                lhs = parts[0].strip()
                loop_var = lhs.split()[-1]
                body_start = j + 1
                break
        
        if body_start != -1:
            for j in range(body_start, len(self.intermediate_code)):
                line = self.intermediate_code[j].strip()
                if line.startswith('goto '):
                    body_end = j - 1
                    break
        
        self.emit(f"for {loop_var} in {iterable}:")
        self.indent_level += 1
        
        if body_start != -1 and body_end != -1:
            for j in range(body_start, body_end + 1):
                body_line = self.intermediate_code[j].strip()
                if body_line and not body_line.endswith(':') and not body_line.startswith('goto'):
                    if body_line.startswith('print '):
                        self.handle_print(body_line)
                    elif '=' in body_line:
                        self.handle_assignment(body_line)
        
        self.indent_level -= 1
        
        for j in range(body_end + 1, len(self.intermediate_code)):
            line = self.intermediate_code[j].strip()
            if line.endswith(':'):
                return j
        
        return body_end + 3

    def convert_expression(self, expr):
        """Convert intermediate code expression to Python"""
        expr = expr.strip()
        
        if expr.startswith('"') and expr.endswith('"'):
            return expr
        
        if expr.startswith('{') and expr.endswith('}'):
            return '[' + expr[1:-1] + ']'
        
        if 'iterator(' in expr or 'next(' in expr or 'has_next(' in expr:
            return expr
        
        return expr

    def save_to_file(self, filename="output.py"):
        """Save generated Python code to a file"""
        with open(filename, 'w') as f:
            f.write('\n'.join(self.python_code))
        print(f"\nPython code saved to {filename}")

    def print_code(self):
        """Print the generated Python code"""
        print("\n=== Generated Python Code ===")
        print('\n'.join(self.python_code))
        print("=" * 30)

    def get_code(self):
        """Return the generated Python code as a string"""
        return '\n'.join(self.python_code)