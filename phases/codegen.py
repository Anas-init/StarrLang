class CodeGenerator():

    def __init__(self, optimized_code):
        self.intermediate_code = optimized_code
        self.python_code = []
        self.indent_level = 0
        self.temp_values = {}
        self.processed_indices = set()

    def generate(self):
        print("\n=== Generating Python Code ===")
        
        self.emit("")
        
        self.collect_temp_values()
        
        i = 0
        while i < len(self.intermediate_code):
            if i in self.processed_indices:
                i += 1
                continue
                
            instruction = self.intermediate_code[i].strip()
            
            if instruction.endswith(':'):
                if self.is_for_loop_start(i):
                    end_idx = self.handle_for_loop(i - 1)
                    for j in range(i - 1, end_idx + 1):
                        self.processed_indices.add(j)
                    i = end_idx
                elif self.is_while_loop_start(i):
                    end_idx = self.handle_while_loop(i)
                    for j in range(i, end_idx + 1):
                        self.processed_indices.add(j)
                    i = end_idx
                else:
                    self.handle_label(instruction, i)
            elif instruction.startswith('if '):
                pass
            elif instruction.startswith('goto '):
                pass
            elif instruction.startswith('print '):
                self.handle_print(instruction)
            elif '= iterator(' in instruction:
                pass
            elif '=' in instruction and not self.is_temp_assignment(instruction):
                self.handle_assignment(instruction)
            
            i += 1
        
        print("Python code generation complete!")
        print("=" * 30)
        return '\n'.join(self.python_code)

    def collect_temp_values(self):
        for instruction in self.intermediate_code:
            instruction = instruction.strip()
            if '=' in instruction and not instruction.endswith(':'):
                parts = instruction.split('=', 1)
                lhs = parts[0].strip()
                rhs = parts[1].strip()
                
                lhs_tokens = lhs.split()
                var_name = lhs_tokens[-1] if lhs_tokens else lhs
                
                if var_name.startswith('t') and len(var_name) > 1 and var_name[1:].isdigit():
                    self.temp_values[var_name] = rhs

    def is_temp_assignment(self, instruction):
        if '=' not in instruction:
            return False
        parts = instruction.split('=', 1)
        lhs = parts[0].strip()
        lhs_tokens = lhs.split()
        var_name = lhs_tokens[-1] if lhs_tokens else lhs
        return var_name.startswith('t') and len(var_name) > 1 and var_name[1:].isdigit()

    def is_for_loop_start(self, index):
        if index <= 0 or index >= len(self.intermediate_code):
            return False
        
        prev_instruction = self.intermediate_code[index - 1].strip()
        if '= iterator(' in prev_instruction:
            return True
        return False

    def is_while_loop_start(self, index):
        if index >= len(self.intermediate_code):
            return False
        
        instruction = self.intermediate_code[index].strip()
        if not instruction.endswith(':'):
            return False
        
        if index + 1 < len(self.intermediate_code):
            next_instruction = self.intermediate_code[index + 1].strip()
            if next_instruction.startswith('if ') and 'has_next' not in next_instruction:
                label_name = instruction[:-1]
                for j in range(index + 1, min(index + 30, len(self.intermediate_code))):
                    line = self.intermediate_code[j].strip()
                    if line == f"goto {label_name}":
                        return True
        
        return False

    def emit(self, code):
        if code:
            self.python_code.append('    ' * self.indent_level + code)
        else:
            self.python_code.append('')

    def handle_assignment(self, instruction):
        parts = instruction.split('=', 1)
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        lhs_tokens = lhs.split()
        var_name = lhs_tokens[-1] if lhs_tokens else lhs
        
        python_rhs = self.convert_expression(rhs, inline_temps=True)
        
        self.emit(f"{var_name} = {python_rhs}")

    def handle_print(self, instruction):
        expr = instruction.split('print ', 1)[1].strip()
        python_expr = self.convert_expression(expr, inline_temps=True)
        self.emit(f"print({python_expr})")

    def handle_label(self, instruction, index):
        label = instruction[:-1]
        if not self.is_for_loop_start(index) and not self.is_while_loop_start(index):
            pass

    def handle_for_loop(self, start_index):
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
                if line.startswith('goto ') and not line.endswith(':'):
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
                    elif '=' in body_line and not self.is_temp_assignment(body_line):
                        self.handle_assignment(body_line)
        
        self.indent_level -= 1
        
        for j in range(body_end + 1, len(self.intermediate_code)):
            line = self.intermediate_code[j].strip()
            if line.endswith(':'):
                return j
        
        return body_end + 3

    def handle_while_loop(self, start_index):
        i = start_index
        
        if i + 1 < len(self.intermediate_code):
            condition_line = self.intermediate_code[i + 1].strip()
            
            if condition_line.startswith('if '):
                condition_parts = condition_line.split('goto')
                condition_expr = condition_parts[0].replace('if', '').strip()
                
                python_condition = self.convert_expression(condition_expr, inline_temps=True)
                
                body_start = i + 4
                body_end = -1
                
                label_name = self.intermediate_code[i].strip()[:-1]
                for j in range(body_start, len(self.intermediate_code)):
                    line = self.intermediate_code[j].strip()
                    if line == f"goto {label_name}":
                        body_end = j - 1
                        break
                
                self.emit(f"while {python_condition}:")
                self.indent_level += 1
                
                if body_start != -1 and body_end != -1:
                    for j in range(body_start, body_end + 1):
                        body_line = self.intermediate_code[j].strip()
                        if body_line and not body_line.endswith(':') and not body_line.startswith('goto'):
                            if body_line.startswith('print '):
                                self.handle_print(body_line)
                            elif '=' in body_line and not self.is_temp_assignment(body_line):
                                self.handle_assignment(body_line)
                
                self.indent_level -= 1
                
                for j in range(body_end + 1, len(self.intermediate_code)):
                    line = self.intermediate_code[j].strip()
                    if line.endswith(':'):
                        return j
                
                return body_end + 2
        
        return i

    def convert_expression(self, expr, inline_temps=False):
        expr = expr.strip()
        
        if inline_temps:
            expr = self.inline_temps(expr)
        
        if expr.startswith('"') and expr.endswith('"'):
            return expr
        
        if expr.isdigit() or (expr.startswith('-') and expr[1:].isdigit()):
            return expr
        
        if expr.startswith('{') and expr.endswith('}'):
            return '[' + expr[1:-1] + ']'
        
        if '[' in expr and ']' in expr:
            parts = expr.split('[', 1)
            var_name = parts[0]
            index_part = parts[1].rsplit(']', 1)[0]
            
            if ':' in index_part:
                colon_parts = index_part.split(':', 1)
                start_str = colon_parts[0]
                end_str = colon_parts[1]
                start = self.convert_expression(start_str.strip(), inline_temps)
                end = self.convert_expression(end_str.strip(), inline_temps)
                return f"{var_name}[{start}:{end}+1]"
            else:
                index = self.convert_expression(index_part, inline_temps)
                return f"{var_name}[{index}]"
        
        for op in ['<=', '>=', '==', '!=', '<', '>']:
            if f' {op} ' in expr:
                parts = expr.split(f' {op} ', 1)
                left = self.convert_expression(parts[0].strip(), inline_temps)
                right = self.convert_expression(parts[1].strip(), inline_temps)
                return f"{left} {op} {right}"
        
        if ' + ' in expr:
            parts = expr.split(' + ', 1)
            left = self.convert_expression(parts[0].strip(), inline_temps)
            right = self.convert_expression(parts[1].strip(), inline_temps)
            return f"{left} + {right}"
        
        if ' - ' in expr:
            parts = expr.split(' - ', 1)
            left = self.convert_expression(parts[0].strip(), inline_temps)
            right = self.convert_expression(parts[1].strip(), inline_temps)
            return f"{left} - {right}"
        
        if ' * ' in expr:
            parts = expr.split(' * ', 1)
            left = self.convert_expression(parts[0].strip(), inline_temps)
            right = self.convert_expression(parts[1].strip(), inline_temps)
            return f"{left} * {right}"
        
        if ' / ' in expr:
            parts = expr.split(' / ', 1)
            left = self.convert_expression(parts[0].strip(), inline_temps)
            right = self.convert_expression(parts[1].strip(), inline_temps)
            return f"{left} // {right}"
        
        if expr.startswith('length('):
            arg = expr.split('length(', 1)[1].rsplit(')', 1)[0]
            return f"len({self.convert_expression(arg, inline_temps)})"
        
        if expr.startswith('size('):
            arg = expr.split('size(', 1)[1].rsplit(')', 1)[0]
            return f"len({self.convert_expression(arg, inline_temps)})"
        
        if 'iterator(' in expr or 'next(' in expr or 'has_next(' in expr:
            return expr
        
        return expr

    def inline_temps(self, expr):
        import re
        
        sorted_temps = sorted(self.temp_values.items(), key=lambda x: len(x[0]), reverse=True)
        
        for temp_var, temp_value in sorted_temps:
            if temp_var in expr:
                pattern = r'\b' + re.escape(temp_var) + r'\b'
                inlined_value = self.convert_expression(temp_value, inline_temps=False)
                expr = re.sub(pattern, inlined_value, expr)
        
        return expr

    def save_to_file(self, filename="output.py"):
        with open(filename, 'w') as f:
            f.write('\n'.join(self.python_code))
        print(f"\nPython code saved to {filename}")

    def print_code(self):
        print("\n=== Generated Python Code ===")
        print('\n'.join(self.python_code))
        print("=" * 30)

    def get_code(self):
        return '\n'.join(self.python_code)