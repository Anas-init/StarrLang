class Optimizer():

    def __init__(self, intermediate_code):
        self.code = intermediate_code.copy()
        self.optimized = False

    def optimize(self):
        print("\n=== Starting Optimization ===")
        print(f"Original instructions: {len(self.code)}")
        
        self.dead_code_elimination()
        self.constant_folding()
        self.copy_propagation()
        self.remove_redundant_labels()
        self.remove_unreachable_code()
        
        print(f"Optimized instructions: {len(self.code)}")
        print("=" * 30)
        
        return self.code

    def dead_code_elimination(self):
        used_vars = set()
        
        def extract_vars_from_expr(expr):
            vars_found = set()
            if '(' in expr:
                func_parts = expr.split('(')
                for part in func_parts[1:]:
                    arg_part = part.split(')')[0]
                    for token in arg_part.replace(',', ' ').replace('(', ' ').replace(')', ' ').split():
                        token = token.strip()
                        if token and ((token[0].isalpha() or token[0] == '_') and (token.replace('_', '').isalnum() or (token.startswith('t') and len(token) > 1 and token[1:].isdigit()))):
                            vars_found.add(token)
            if '[' in expr:
                arr_name = expr.split('[')[0].strip()
                vars_found.add(arr_name)
                bracket_start = expr.find('[')
                bracket_end = expr.find(']', bracket_start)
                if bracket_end > bracket_start:
                    index_part = expr[bracket_start+1:bracket_end]
                    if ':' in index_part:
                        for part in index_part.split(':'):
                            part = part.strip()
                            if part and not part.isdigit() and not (part.startswith('-') and part[1:].isdigit()):
                                if (part[0].isalpha() or part[0] == '_') and (part.replace('_', '').isalnum() or (part.startswith('t') and len(part) > 1 and part[1:].isdigit())):
                                    vars_found.add(part)
                    else:
                        index_part = index_part.strip()
                        if index_part and not index_part.isdigit() and not (index_part.startswith('-') and index_part[1:].isdigit()):
                            if (index_part[0].isalpha() or index_part[0] == '_') and (index_part.replace('_', '').isalnum() or (index_part.startswith('t') and len(index_part) > 1 and index_part[1:].isdigit())):
                                vars_found.add(index_part)
            for op in [' + ', ' - ', ' * ', ' / ', ' < ', ' > ', ' <= ', ' >= ', ' == ', ' != ']:
                if op in expr:
                    parts = expr.split(op, 1)
                    for part in parts:
                        part = part.strip()
                        if not (part.startswith('"') or part.startswith('{')):
                            for token in part.split():
                                token = token.strip()
                                if token and ((token[0].isalpha() or token[0] == '_') and (token.replace('_', '').isalnum() or (token.startswith('t') and len(token) > 1 and token[1:].isdigit()))):
                                    vars_found.add(token)
                    break
            if not any(op in expr for op in [' + ', ' - ', ' * ', ' / ', ' < ', ' > ', ' <= ', ' >= ', ' == ', ' != ', '[', '(']):
                expr_clean = expr.strip()
                if expr_clean and not expr_clean.startswith('"') and not expr_clean.startswith('{') and not expr_clean.isdigit():
                    if (expr_clean[0].isalpha() or expr_clean[0] == '_') and (expr_clean.replace('_', '').isalnum() or (expr_clean.startswith('t') and len(expr_clean) > 1 and expr_clean[1:].isdigit())):
                        vars_found.add(expr_clean)
            return vars_found
        
        for i in range(len(self.code) - 1, -1, -1):
            instruction = self.code[i].strip()
            
            if instruction.startswith('print '):
                expr = instruction.split('print ', 1)[1].strip()
                used_vars.update(extract_vars_from_expr(expr))
            
            if instruction.startswith('if '):
                condition = instruction.split('goto')[0].replace('if', '').strip()
                used_vars.update(extract_vars_from_expr(condition))
        
        changed = True
        iterations = 0
        max_iterations = 10
        while changed and iterations < max_iterations:
            changed = False
            iterations += 1
            for i in range(len(self.code) - 1, -1, -1):
                instruction = self.code[i].strip()
                
                if '=' in instruction and not instruction.endswith(':'):
                    parts = instruction.split('=', 1)
                    if len(parts) == 2:
                        lhs = parts[0].strip()
                        rhs = parts[1].strip()
                        lhs_tokens = lhs.split()
                        var_name = lhs_tokens[-1] if lhs_tokens else ''
                        
                        if var_name in used_vars:
                            rhs_vars = extract_vars_from_expr(rhs)
                            if rhs_vars - used_vars:
                                used_vars.update(rhs_vars)
                                changed = True
                
                if instruction.startswith('print '):
                    expr = instruction.split('print ', 1)[1].strip()
                    new_vars = extract_vars_from_expr(expr)
                    if new_vars - used_vars:
                        used_vars.update(new_vars)
                        changed = True
                
                if instruction.startswith('if '):
                    condition = instruction.split('goto')[0].replace('if', '').strip()
                    new_vars = extract_vars_from_expr(condition)
                    if new_vars - used_vars:
                        used_vars.update(new_vars)
                        changed = True
        
        new_code = []
        for instruction in self.code:
            keep = True
            
            if '=' in instruction and not instruction.strip().endswith(':'):
                parts = instruction.split('=', 1)
                if len(parts) == 2:
                    lhs = parts[0].strip()
                    tokens = lhs.split()
                    var_name = tokens[-1] if tokens else ''
                    
                    if 'iterator(' in instruction or 'next(' in instruction:
                        keep = True
                    elif var_name.startswith('t') and len(var_name) > 1 and var_name[1:].isdigit():
                        keep = var_name in used_vars
                    elif var_name and var_name in used_vars:
                        keep = True
                    elif var_name:
                        if instruction.strip().startswith('string ') and ' = next(' in instruction:
                            keep = True
                        else:
                            keep = False
            
            if keep:
                new_code.append(instruction)
        
        if len(new_code) != len(self.code):
            self.optimized = True
        self.code = new_code

    def constant_folding(self):
        pass

    def copy_propagation(self):
        copies = {}
        new_code = []
        
        for instruction in self.code:
            modified_instruction = instruction
            
            if '=' in instruction and not instruction.strip().endswith(':'):
                parts = instruction.split('=', 1)
                if len(parts) == 2:
                    lhs = parts[0].strip()
                    rhs = parts[1].strip()
                    
                    lhs_tokens = lhs.split()
                    var_name = lhs_tokens[-1] if lhs_tokens else ''
                    
                    if rhs and not rhs.startswith('"') and not rhs.startswith('{') and '(' not in rhs and '[' not in rhs and ':' not in rhs:
                        rhs_clean = rhs.strip()
                        if not any(op in rhs_clean for op in [' + ', ' - ', ' * ', ' / ', ' < ', ' > ', ' <= ', ' >= ', ' == ', ' != ']):
                            if rhs_clean.replace('_', '').replace('t', '').isalnum() or (rhs_clean.startswith('t') and len(rhs_clean) > 1 and rhs_clean[1:].isdigit()):
                                if rhs_clean not in copies or copies[rhs_clean] != var_name:
                                    copies[var_name] = rhs_clean
                    if var_name in copies:
                        del copies[var_name]
            
            for var, value in copies.items():
                if var in modified_instruction:
                    import re
                    pattern = r'\b' + re.escape(var) + r'\b'
                    if '=' in modified_instruction:
                        parts = modified_instruction.split('=', 1)
                        if len(parts) == 2 and var not in parts[0] and value != parts[0].strip().split()[-1]:
                            modified_instruction = re.sub(pattern, value, modified_instruction)
                    else:
                        modified_instruction = re.sub(pattern, value, modified_instruction)
            
            new_code.append(modified_instruction)
        
        if new_code != self.code:
            self.optimized = True
        self.code = new_code

    def remove_redundant_labels(self):
        labels = set()
        for instruction in self.code:
            if instruction.strip().endswith(':'):
                label = instruction.strip()[:-1]
                labels.add(label)
        
        used_labels = set()
        for instruction in self.code:
            if 'goto' in instruction:
                parts = instruction.split()
                for part in parts:
                    if part.startswith('L') and part in labels:
                        used_labels.add(part)
        
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
        reachable = set()
        labels = {}
        
        for i, instruction in enumerate(self.code):
            if instruction.strip().endswith(':'):
                label = instruction.strip()[:-1]
                labels[label] = i
        
        to_visit = [0]
        while to_visit:
            i = to_visit.pop(0)
            if i >= len(self.code) or i in reachable:
                continue
            
            reachable.add(i)
            instruction = self.code[i].strip()
            
            if instruction.endswith(':'):
                if i + 1 < len(self.code):
                    to_visit.append(i + 1)
            elif instruction.startswith('goto '):
                label = instruction.split('goto')[1].strip()
                if label in labels:
                    to_visit.append(labels[label])
            elif instruction.startswith('if '):
                parts = instruction.split('goto')
                if len(parts) == 2:
                    label = parts[1].strip()
                    if label in labels:
                        to_visit.append(labels[label])
                if i + 1 < len(self.code):
                    to_visit.append(i + 1)
            else:
                if i + 1 < len(self.code):
                    to_visit.append(i + 1)
        
        new_code = []
        for i, instruction in enumerate(self.code):
            if i in reachable:
                new_code.append(instruction)
        
        if len(new_code) != len(self.code):
            self.optimized = True
        self.code = new_code

    def print_optimized_code(self):
        print("\n=== Optimized Intermediate Code ===")
        for i, instruction in enumerate(self.code):
            print(f"{i+1:3}. {instruction}")
        print("=" * 35)

    def get_code(self):
        return self.code

    def peephole_optimization(self):
        new_code = []
        i = 0
        
        while i < len(self.code):
            if i < len(self.code) - 1:
                curr = self.code[i].strip()
                next_instr = self.code[i + 1].strip()
                
                if curr.startswith('goto ') and next_instr.endswith(':'):
                    label = curr.split()[1]
                    next_label = next_instr[:-1]
                    if label == next_label:
                        i += 1
                        continue
            
            new_code.append(self.code[i])
            i += 1
        
        if len(new_code) != len(self.code):
            self.optimized = True
        self.code = new_code