class Interpreter():

    def __init__(self, optimized_code):
        self.intermediate_code = optimized_code
        self.variables = {}
        self.pc = 0
        self.labels = {}

    def execute(self):
        print("\n=== Executing Program ===")
        print("Output:")
        print("-" * 30)
        
        self.find_labels()
        
        self.pc = 0
        while self.pc < len(self.intermediate_code):
            instruction = self.intermediate_code[self.pc].strip()
            
            if not instruction or instruction.endswith(':'):
                self.pc += 1
                continue
            
            old_pc = self.pc
            self.execute_instruction(instruction)
            if self.pc == old_pc:
                self.pc += 1
        
        print("-" * 30)
        print("Program execution complete!")
        print("=" * 30)

    def find_labels(self):
        for i, instruction in enumerate(self.intermediate_code):
            instruction = instruction.strip()
            if instruction.endswith(':'):
                label_name = instruction[:-1]
                self.labels[label_name] = i

    def execute_instruction(self, instruction):
        if instruction.startswith('print '):
            self.execute_print(instruction)
        elif instruction.startswith('if '):
            self.execute_if(instruction)
        elif instruction.startswith('goto '):
            self.execute_goto(instruction)
        elif '=' in instruction:
            self.execute_assignment(instruction)

    def execute_assignment(self, instruction):
        parts = instruction.split('=', 1)
        if len(parts) != 2:
            return
        
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        lhs_tokens = lhs.split()
        var_name = lhs_tokens[-1] if lhs_tokens else ''
        
        if not var_name:
            return
        
        value = self.evaluate_expression(rhs)
        if value is not None:
            self.variables[var_name] = value

    def execute_print(self, instruction):
        expr = instruction.split('print ', 1)[1].strip()
        value = self.evaluate_expression(expr)
        
        if isinstance(value, list):
            print(value)
        else:
            print(value)

    def execute_if(self, instruction):
        parts = instruction.split('goto')
        condition = parts[0].replace('if', '').strip()
        label = parts[1].strip()
        
        if self.evaluate_condition(condition):
            if label in self.labels:
                self.pc = self.labels[label]

    def execute_goto(self, instruction):
        label = instruction.split('goto')[1].strip()
        
        if label in self.labels:
            self.pc = self.labels[label]

    def evaluate_expression(self, expr):
        expr = expr.strip()
        
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        if isinstance(expr, int):
            return expr

        if isinstance(expr, bool):
            return expr

        if isinstance(expr, str):
            if expr.isdigit() or (expr.startswith('-') and expr[1:].isdigit()):
                return int(expr)

        
        if expr.startswith('{') and expr.endswith('}'):
            elements = expr[1:-1].split(',')
            return [self.evaluate_expression(e.strip()) for e in elements if e.strip()]
        
        if '[' in expr and ':' in expr and ']' in expr and 'iterator' not in expr:
            parts = expr.split('[')
            var_name = parts[0].strip()
            slice_part = parts[1].split(']')[0]
            
            if ':' in slice_part:
                start_str, end_str = slice_part.split(':', 1)
                start = self.evaluate_expression(start_str.strip())
                end = self.evaluate_expression(end_str.strip())
                
                if isinstance(start, str) and start.isdigit():
                    start = int(start)
                elif isinstance(start, str):
                    start_val = self.variables.get(start)
                    if isinstance(start_val, int):
                        start = start_val
                    elif isinstance(start_val, str) and start_val.isdigit():
                        start = int(start_val)
                
                if isinstance(end, str) and end.isdigit():
                    end = int(end)
                elif isinstance(end, str):
                    end_val = self.variables.get(end)
                    if isinstance(end_val, int):
                        end = end_val
                    elif isinstance(end_val, str) and end_val.isdigit():
                        end = int(end_val)
                
                var_value = self.variables.get(var_name)
                if var_value is not None:
                    if isinstance(start, int) and isinstance(end, int):
                        if 0 <= start <= end < len(var_value):
                            return var_value[start:end+1]
                        elif 0 <= start < len(var_value):
                            return var_value[start:min(end+1, len(var_value))]
            return None
        
        if '[' in expr and ']' in expr and ':' not in expr:
            var_name = expr.split('[')[0].strip()
            index_expr = expr.split('[')[1].split(']')[0]
            index = self.evaluate_expression(index_expr)
            
            if isinstance(index, str) and index.isdigit():
                index = int(index)
            elif isinstance(index, str):
                index_val = self.variables.get(index)
                if isinstance(index_val, int):
                    index = index_val
                elif isinstance(index_val, str) and index_val.isdigit():
                    index = int(index_val)
            
            var_value = self.variables.get(var_name)
            if var_value is not None and isinstance(index, int):
                if 0 <= index < len(var_value):
                    return var_value[index]
            return None
        
        if ' + ' in expr:
            parts = expr.split(' + ', 1)
            left = self.evaluate_expression(parts[0].strip())
            right = self.evaluate_expression(parts[1].strip())
            
            if isinstance(left, int) and isinstance(right, int):
                return left + right
            elif isinstance(left, str) and isinstance(right, str):
                return left + right
            else:
                return str(left) + str(right)
        
        if ' - ' in expr:
            parts = expr.split(' - ', 1)
            left = self.evaluate_expression(parts[0].strip())
            right = self.evaluate_expression(parts[1].strip())
            
            if isinstance(left, int) and isinstance(right, int):
                return left - right
            return 0
        
        if ' * ' in expr:
            parts = expr.split(' * ', 1)
            left = self.evaluate_expression(parts[0].strip())
            right = self.evaluate_expression(parts[1].strip())
            
            if isinstance(left, int) and isinstance(right, int):
                return left * right
            return 0
        
        if ' / ' in expr:
            parts = expr.split(' / ', 1)
            left = self.evaluate_expression(parts[0].strip())
            right = self.evaluate_expression(parts[1].strip())
            
            if isinstance(left, int) and isinstance(right, int) and right != 0:
                return left // right
            return 0
        
        for op in ['<=', '>=', '==', '!=', '<', '>']:
            if op in expr:
                if f' {op} ' in expr:
                    parts = expr.split(f' {op} ', 1)
                elif expr.startswith(op):
                    continue
                else:
                    idx = expr.find(op)
                    if idx > 0:
                        parts = [expr[:idx].strip(), expr[idx+len(op):].strip()]
                    else:
                        continue
                
                left = self.evaluate_expression(parts[0].strip())
                right = self.evaluate_expression(parts[1].strip())
                
                if isinstance(left, str) and left.isdigit():
                    left = int(left)
                if isinstance(right, str) and right.isdigit():
                    right = int(right)
                
                if op == '<':
                    return left < right
                elif op == '>':
                    return left > right
                elif op == '<=':
                    return left <= right
                elif op == '>=':
                    return left >= right
                elif op == '==':
                    return left == right
                elif op == '!=':
                    return left != right
                break
        
        if expr.startswith('iterator('):
            var_name = expr.split('iterator(')[1].split(')')[0]
            var_value = self.variables.get(var_name)
            if var_value is not None:
                return {'iterable': var_value, 'index': 0}
            return None
        
        if expr.startswith('next('):
            iter_name = expr.split('next(')[1].split(')')[0]
            iterator = self.variables.get(iter_name)
            if iterator and isinstance(iterator, dict):
                iterable = iterator['iterable']
                index = iterator['index']
                if index < len(iterable):
                    element = iterable[index]
                    self.variables[iter_name]['index'] += 1
                    return element
            return None
        
        if expr.startswith('length('):
            arg_expr = expr.split('length(')[1].rsplit(')', 1)[0]
            arg_value = self.evaluate_expression(arg_expr)
            if arg_value is not None:
                return len(arg_value)
            return 0
        
        if expr.startswith('size('):
            arg_expr = expr.split('size(')[1].rsplit(')', 1)[0]
            arg_value = self.evaluate_expression(arg_expr)
            if arg_value is not None:
                return len(arg_value)
            return 0
        
        if expr in self.variables:
            return self.variables[expr]
        
        if expr.isdigit() or (expr.startswith('-') and expr[1:].isdigit()):
            return int(expr)
        
        return expr

    def evaluate_condition(self, condition):
        condition = condition.strip()
        
        if condition.startswith('has_next('):
            iter_name = condition.split('has_next(')[1].split(')')[0].strip()
            iterator = self.variables.get(iter_name)
            if iterator and isinstance(iterator, dict):
                return iterator['index'] < len(iterator['iterable'])
            return False
        
        result = self.evaluate_expression(condition)
        
        if isinstance(result, bool):
            return result
        
        if isinstance(result, int):
            return result != 0
        
        if isinstance(result, str):
            return len(result) > 0
        
        return False

    def print_variables(self):
        print("\n=== Variable State ===")
        for var, value in self.variables.items():
            if not isinstance(value, dict):
                print(f"{var} = {value}")
        print("=" * 25)