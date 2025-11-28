class CodeGenerator():

    def __init__(self, optimized_code):
        self.intermediate_code = optimized_code
        self.python_code = []
        self.indent_level = 0

    def generate(self):
        """Generate Python code from intermediate code"""
        print("\n=== Generating Python Code ===")
        
        # Add header comment
        self.emit("# Generated Python Code")
        self.emit("")
        
        # Process each instruction
        i = 0
        while i < len(self.intermediate_code):
            instruction = self.intermediate_code[i].strip()
            
            if instruction.endswith(':'):
                # Label - add comment and handle loop structure
                self.handle_label(instruction, i)
            elif instruction.startswith('if '):
                # Conditional jump - part of loop structure
                pass  # Handled by loop detection
            elif instruction.startswith('goto '):
                # Unconditional jump - part of loop structure
                pass  # Handled by loop detection
            elif instruction.startswith('print '):
                self.handle_print(instruction)
            elif '= iterator(' in instruction:
                # Start of for loop - detect and handle entire loop
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
        # Parse: typename name = value  OR  name = value
        parts = instruction.split('=', 1)
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        # Remove type declaration if present
        lhs_tokens = lhs.split()
        var_name = lhs_tokens[-1] if lhs_tokens else lhs
        
        # Convert RHS
        python_rhs = self.convert_expression(rhs)
        
        self.emit(f"{var_name} = {python_rhs}")

    def handle_print(self, instruction):
        """Convert print statement to Python"""
        # Parse: print expression
        expr = instruction.split('print ', 1)[1].strip()
        
        # Check if it's a slice expression
        if '[' in expr and ':' in expr:
            # Format: var[start:end]
            var_name = expr.split('[')[0]
            slice_part = expr.split('[')[1].split(']')[0]
            start, end = slice_part.split(':')
            start = int(start)
            end = int(end)
            
            # Python uses exclusive end, we use inclusive, so add 1
            self.emit(f"print({var_name}[{start}:{end+1}])")
        else:
            python_expr = self.convert_expression(expr)
            self.emit(f"print({python_expr})")

    def handle_label(self, instruction, index):
        """Handle label - usually part of loop structure"""
        # Labels are handled in loop detection, just add comment
        label = instruction[:-1]
        self.emit(f"# {label}")

    def handle_for_loop(self, start_index):
        """Detect and convert for loop structure to Python for loop"""
        # Loop pattern:
        # t0 = iterator(iterable)
        # L_start:
        # if has_next(t0) goto L_body
        # goto L_end
        # L_body:
        # string var = next(t0)
        # [body statements]
        # goto L_start
        # L_end:
        
        i = start_index
        iterator_line = self.intermediate_code[i].strip()
        
        # Extract iterable name
        # Format: tX = iterator(iterable_name)
        iterable = iterator_line.split('iterator(')[1].split(')')[0]
        
        # Skip to the "string var = next(t0)" line to get loop variable
        loop_var = None
        body_start = -1
        body_end = -1
        
        # Find the loop body
        for j in range(i, len(self.intermediate_code)):
            line = self.intermediate_code[j].strip()
            if 'next(' in line and '=' in line:
                # Found loop variable assignment
                parts = line.split('=', 1)
                lhs = parts[0].strip()
                loop_var = lhs.split()[-1]
                body_start = j + 1
                break
        
        # Find body end (next goto statement after body_start)
        if body_start != -1:
            for j in range(body_start, len(self.intermediate_code)):
                line = self.intermediate_code[j].strip()
                if line.startswith('goto '):
                    body_end = j - 1
                    break
        
        # Generate Python for loop
        self.emit(f"for {loop_var} in {iterable}:")
        self.indent_level += 1
        
        # Generate body statements
        if body_start != -1 and body_end != -1:
            for j in range(body_start, body_end + 1):
                body_line = self.intermediate_code[j].strip()
                if body_line and not body_line.endswith(':') and not body_line.startswith('goto'):
                    if body_line.startswith('print '):
                        self.handle_print(body_line)
                    elif '=' in body_line:
                        self.handle_assignment(body_line)
        
        self.indent_level -= 1
        
        # Return the index of the last line of the loop (L_end:)
        for j in range(body_end + 1, len(self.intermediate_code)):
            line = self.intermediate_code[j].strip()
            if line.endswith(':'):
                return j
        
        return body_end + 3  # Skip to after the loop

    def convert_expression(self, expr):
        """Convert intermediate code expression to Python"""
        expr = expr.strip()
        
        # Handle string literals (already in quotes)
        if expr.startswith('"') and expr.endswith('"'):
            return expr
        
        # Handle array literals: {a, b, c} -> [a, b, c]
        if expr.startswith('{') and expr.endswith('}'):
            return '[' + expr[1:-1] + ']'
        
        # Handle function calls (iterator, next, has_next)
        if 'iterator(' in expr or 'next(' in expr or 'has_next(' in expr:
            # These are internal and shouldn't appear in final code
            return expr
        
        # Handle identifiers and other expressions
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