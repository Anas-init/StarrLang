class Optimizer():

    def __init__(self, intermediate_code):
        self.code = intermediate_code.copy()
        self.optimized = False

    def optimize(self):
        """Apply all optimization passes"""
        print("\n=== Starting Optimization ===")
        print(f"Original instructions: {len(self.code)}")
        
        # Apply optimization passes
        self.dead_code_elimination()
        self.constant_folding()
        self.copy_propagation()
        self.remove_redundant_labels()
        self.remove_unreachable_code()
        
        print(f"Optimized instructions: {len(self.code)}")
        print("=" * 30)
        
        return self.code

    def dead_code_elimination(self):
        """Remove unused variable declarations and assignments"""
        # Track which variables are used
        used_vars = set()
        
        # First pass: find all used variables
        for instruction in self.code:
            # Check for variable usage in right-hand side
            if '=' in instruction and not instruction.strip().endswith(':'):
                # Skip labels
                parts = instruction.split('=', 1)
                if len(parts) == 2:
                    rhs = parts[1].strip()
                    # Extract variable names from rhs
                    tokens = rhs.replace('(', ' ').replace(')', ' ').replace(',', ' ').split()
                    for token in tokens:
                        if token and not token.startswith('"') and not token.isdigit() and token not in ['{', '}', 'iterator', 'next', 'has_next']:
                            used_vars.add(token)
            
            # Check for print statements
            if instruction.strip().startswith('print '):
                var = instruction.split('print ', 1)[1].strip()
                # Extract base variable name if it's a slice
                if '[' in var:
                    var = var.split('[')[0]
                used_vars.add(var)
            
            # Check for if conditions
            if instruction.strip().startswith('if '):
                parts = instruction.split()
                for part in parts:
                    if part and not part.startswith('goto') and not part.startswith('L') and part not in ['if', 'has_next']:
                        if '(' in part:
                            var = part.split('(')[1].replace(')', '')
                            used_vars.add(var)
        
        # Second pass: remove unused assignments
        new_code = []
        for instruction in self.code:
            keep = True
            
            # Check if it's an assignment or declaration
            if '=' in instruction and not instruction.strip().endswith(':'):
                parts = instruction.split('=', 1)
                if len(parts) == 2:
                    lhs = parts[0].strip()
                    # Extract variable name (handle "type name" format)
                    tokens = lhs.split()
                    var_name = tokens[-1] if tokens else ''
                    
                    # Remove if variable is never used and not a temp for iterator
                    if var_name and var_name not in used_vars and not instruction.strip().startswith('string ' + var_name + ' = next'):
                        keep = False
            
            if keep:
                new_code.append(instruction)
        
        if len(new_code) != len(self.code):
            self.optimized = True
        self.code = new_code

    def constant_folding(self):
        """Fold constant expressions (limited for string operations)"""
        # For this simple language, we mainly handle string literal assignments
        # Could be extended for arithmetic if added to language
        pass

    def copy_propagation(self):
        """Propagate copy assignments (x = y, then use x -> use y)"""
        # Build a map of simple copies
        copies = {}
        new_code = []
        
        for instruction in self.code:
            modified_instruction = instruction
            
            # Detect simple copy: x = y (where y is an identifier)
            if '=' in instruction and not instruction.strip().endswith(':'):
                parts = instruction.split('=', 1)
                if len(parts) == 2:
                    lhs = parts[0].strip()
                    rhs = parts[1].strip()
                    
                    # Extract variable name from lhs
                    lhs_tokens = lhs.split()
                    var_name = lhs_tokens[-1] if lhs_tokens else ''
                    
                    # Check if rhs is a simple identifier (not a literal, not a complex expression)
                    if rhs and not rhs.startswith('"') and not rhs.startswith('{') and not '(' in rhs and not '[' in rhs:
                        if rhs.replace('_', '').replace('t', '').isalnum():
                            copies[var_name] = rhs
            
            # Replace uses of copied variables
            for var, value in copies.items():
                # Only replace whole word matches
                if var in modified_instruction:
                    # Simple word boundary check
                    import re
                    pattern = r'\b' + re.escape(var) + r'\b'
                    # Don't replace on left side of assignment
                    if '=' in modified_instruction:
                        parts = modified_instruction.split('=', 1)
                        if len(parts) == 2 and var not in parts[0]:
                            modified_instruction = re.sub(pattern, value, modified_instruction)
                    else:
                        modified_instruction = re.sub(pattern, value, modified_instruction)
            
            new_code.append(modified_instruction)
        
        if new_code != self.code:
            self.optimized = True
        self.code = new_code

    def remove_redundant_labels(self):
        """Remove labels that are never jumped to"""
        # Find all labels
        labels = set()
        for instruction in self.code:
            if instruction.strip().endswith(':'):
                label = instruction.strip()[:-1]
                labels.add(label)
        
        # Find labels that are actually used
        used_labels = set()
        for instruction in self.code:
            if 'goto' in instruction:
                parts = instruction.split()
                for part in parts:
                    if part.startswith('L') and part in labels:
                        used_labels.add(part)
        
        # Remove unused labels
        new_code = []
        for instruction in self.code:
            if instruction.strip().endswith(':'):
                label = instruction.strip()[:-1]
                if label in used_labels:
                    new_code.append(instruction)
                else:
                    self.optimized = True
            else:
                new_code.append(instruction)
        
        self.code = new_code

    def remove_unreachable_code(self):
        """Remove code that can never be executed"""
        new_code = []
        reachable = True
        
        for instruction in self.code:
            # Check if we hit a label (code becomes reachable again)
            if instruction.strip().endswith(':'):
                reachable = True
                new_code.append(instruction)
            # If code is reachable, keep it
            elif reachable:
                new_code.append(instruction)
                # After unconditional goto, code becomes unreachable
                if instruction.strip().startswith('goto ') and not instruction.strip().startswith('goto L'):
                    # Actually, in our case all gotos are unconditional
                    pass
            else:
                # Unreachable code, skip it
                self.optimized = True
        
        self.code = new_code

    def print_optimized_code(self):
        """Print the optimized intermediate code"""
        print("\n=== Optimized Intermediate Code ===")
        for i, instruction in enumerate(self.code):
            print(f"{i+1:3}. {instruction}")
        print("=" * 35)

    def get_code(self):
        """Return the optimized intermediate code"""
        return self.code

    def peephole_optimization(self):
        """Apply peephole optimizations on small instruction windows"""
        new_code = []
        i = 0
        
        while i < len(self.code):
            # Check for redundant goto chains: goto L1; L1: goto L2 -> goto L2
            if i < len(self.code) - 1:
                curr = self.code[i].strip()
                next_instr = self.code[i + 1].strip()
                
                if curr.startswith('goto ') and next_instr.endswith(':'):
                    label = curr.split()[1]
                    next_label = next_instr[:-1]
                    if label == next_label:
                        # Skip redundant goto
                        i += 1
                        continue
            
            new_code.append(self.code[i])
            i += 1
        
        if len(new_code) != len(self.code):
            self.optimized = True
        self.code = new_code