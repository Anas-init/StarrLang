class Interpreter():

    def __init__(self, optimized_code):
        self.intermediate_code = optimized_code
        self.variables = {}
        self.pc = 0  # Program counter
        self.labels = {}  # Label positions

    def execute(self):
        """Execute the intermediate code"""
        print("\n=== Executing Program ===")
        print("Output:")
        print("-" * 30)
        
        # First pass: find all labels
        self.find_labels()
        
        # Second pass: execute instructions
        self.pc = 0
        while self.pc < len(self.intermediate_code):
            instruction = self.intermediate_code[self.pc].strip()
            
            # Skip empty lines and labels
            if not instruction or instruction.endswith(':'):
                self.pc += 1
                continue
            
            # Execute instruction
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
        # Parse: typename name = value  OR  name = value
        parts = instruction.split('=', 1)
        lhs = parts[0].strip()
        rhs = parts[1].strip()
        
        # Remove type declaration if present
        lhs_tokens = lhs.split()
        var_name = lhs_tokens[-1]
        
        # Evaluate RHS and store
        value = self.evaluate_expression(rhs)
        self.variables[var_name] = value

    def execute_print(self, instruction):
        """Execute a print statement"""
        # Parse: print expression
        expr = instruction.split('print ', 1)[1].strip()
        
        # Evaluate and print
        value = self.evaluate_expression(expr)
        
        # Handle printing lists/arrays
        if isinstance(value, list):
            # Print array elements
            print(value)
        else:
            print(value)

    def execute_if(self, instruction):
        """Execute conditional jump"""
        # Parse: if has_next(iterator) goto label
        parts = instruction.split('goto')
        condition = parts[0].replace('if', '').strip()
        label = parts[1].strip()
        
        # Evaluate condition
        if self.evaluate_condition(condition):
            # Jump to label
            if label in self.labels:
                self.pc = self.labels[label]

    def execute_goto(self, instruction):
        """Execute unconditional jump"""
        # Parse: goto label
        label = instruction.split('goto')[1].strip()
        
        # Jump to label
        if label in self.labels:
            self.pc = self.labels[label]

    def evaluate_expression(self, expr):
        """Evaluate an expression and return its value"""
        expr = expr.strip()
        
        # String literal
        if expr.startswith('"') and expr.endswith('"'):
            return expr[1:-1]  # Remove quotes
        
        # Array literal: {a, b, c}
        if expr.startswith('{') and expr.endswith('}'):
            elements = expr[1:-1].split(',')
            return [self.evaluate_expression(e.strip()) for e in elements]
        
        # Slice expression: var[start:end]
        if '[' in expr and ':' in expr:
            var_name = expr.split('[')[0]
            slice_part = expr.split('[')[1].split(']')[0]
            start, end = slice_part.split(':')
            start = int(start)
            end = int(end)
            
            var_value = self.variables.get(var_name)
            if var_value is not None:
                # Return slice (inclusive end)
                return var_value[start:end+1]
            return None
        
        # Iterator creation: iterator(var)
        if expr.startswith('iterator('):
            var_name = expr.split('iterator(')[1].split(')')[0]
            var_value = self.variables.get(var_name)
            if var_value is not None:
                # Return an iterator object (we'll use a tuple: (iterable, index))
                return {'iterable': var_value, 'index': 0}
            return None
        
        # Next element: next(iterator)
        if expr.startswith('next('):
            iter_name = expr.split('next(')[1].split(')')[0]
            iterator = self.variables.get(iter_name)
            if iterator and isinstance(iterator, dict):
                iterable = iterator['iterable']
                index = iterator['index']
                if index < len(iterable):
                    element = iterable[index]
                    # Update iterator index
                    self.variables[iter_name]['index'] += 1
                    return element
            return None
        
        # Variable reference
        if expr in self.variables:
            return self.variables[expr]
        
        # Number
        if expr.isdigit():
            return int(expr)
        
        # Unknown
        return expr

    def evaluate_condition(self, condition):
        """Evaluate a boolean condition"""
        condition = condition.strip()
        
        # has_next(iterator)
        if condition.startswith('has_next('):
            iter_name = condition.split('has_next(')[1].split(')')[0]
            iterator = self.variables.get(iter_name)
            if iterator and isinstance(iterator, dict):
                return iterator['index'] < len(iterator['iterable'])
            return False
        
        # Other conditions can be added here
        return False

    def print_variables(self):
        """Print all variables for debugging"""
        print("\n=== Variable State ===")
        for var, value in self.variables.items():
            if not isinstance(value, dict):  # Skip internal iterator objects
                print(f"{var} = {value}")
        print("=" * 25)