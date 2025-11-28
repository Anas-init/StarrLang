class Interpreter():

    def __init__(self, optimized_code):
        self.intermediate_code = optimized_code
        self.variables = {}
        self.pc = 0
        self.labels = {}

    def execute(self):
        """Execute the intermediate code"""
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
            
            self.execute_instruction(instruction)
            self.pc += 1
        
        print("-" * 30)
        print("Program execution complete!")
        print("=" * 30)

    def find_labels(self):
        """Build a map of label names to their positions"""
        for i, instruction in enumerate(self.intermediate_code):
            instruction = instruction.strip()
            if instruction.endswith(':'):
                label_name = instruction[:-1]
                self.labels[label_name] = i

    def execute_instruction(self, instruction):
        """Execute a single instruction"""
        if instruction.startswith('print '):
            self.execute_print(instruction)
        elif instruction.startswith('if '):
            self.execute_if(instruction)
        elif instruction.startswith('goto '):
            self.execute_goto(instruction)
        elif '=' in instruction:
            self.execute_assignment(instruction)

    def execute_assignment(self, instruction):
        """Execute an assignment"""
        parts = instruction.split('=', 1)
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        lhs_tokens = lhs.split()
        var_name = lhs_tokens[-1]
        
        value = self.evaluate_expression(rhs)
        self.variables[var_name] = value

    def execute_print(self, instruction):
        """Execute a print statement"""
        expr = instruction.split('print ', 1)[1].strip()
        
        value = self.evaluate_expression(expr)
        
        if isinstance(value, list):
            print(value)
        else:
            print(value)

    def execute_if(self, instruction):
        """Execute conditional jump"""
        parts = instruction.split('goto')
        condition = parts[0].replace('if', '').strip()
        label = parts[1].strip()
        
        if self.evaluate_condition(condition):
            if label in self.labels:
                self.pc = self.labels[label]

    def execute_goto(self, instruction):
        """Execute unconditional jump"""
        label = instruction.split('goto')[1].strip()
        
        if label in self.labels:
            self.pc = self.labels[label]

    def evaluate_expression(self, expr):
        """Evaluate an expression and return its value"""
        expr = expr.strip()
        
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]
        
        if expr.startswith('{') and expr.endswith('}'):
            elements = expr[1:-1].split(',')
            return [self.evaluate_expression(e.strip()) for e in elements]
        
        if '[' in expr and ':' in expr:
            var_name = expr.split('[')[0]
            slice_part = expr.split('[')[1].split(']')[0]
            start, end = slice_part.split(':')
            start = int(start)
            end = int(end)
            
            var_value = self.variables.get(var_name)
            if var_value is not None:
                return var_value[start:end+1]
            return None
        
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
        
        if expr in self.variables:
            return self.variables[expr]
        
        if expr.isdigit():
            return int(expr)
        
        return expr

    def evaluate_condition(self, condition):
        """Evaluate a boolean condition"""
        condition = condition.strip()
        
        if condition.startswith('has_next('):
            iter_name = condition.split('has_next(')[1].split(')')[0]
            iterator = self.variables.get(iter_name)
            if iterator and isinstance(iterator, dict):
                return iterator['index'] < len(iterator['iterable'])
            return False
        
        return False

    def print_variables(self):
        """Print all variables for debugging"""
        print("\n=== Variable State ===")
        for var, value in self.variables.items():
            if not isinstance(value, dict):
                print(f"{var} = {value}")
        print("=" * 25)