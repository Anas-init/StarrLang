import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
from io import StringIO

from phases.intermediate import IntermediateCode
from phases.lexical import LexicalAnalysis
from phases.semantic import SemanticAnalysis
from phases.syntax import SyntaxAnalysis
from phases.optimizer import Optimizer
from phases.codegen import CodeGenerator
from phases.interpreter import Interpreter


class CompilerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Starrlang")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        self.tokens = [
            ("KEYWORD",    r'\b(string|int|array|for|while|if|else|return|in)\b'),
            ("COUT",       r'\bcout\b'),
            ("SHL",        r'<<'),
            ("EQ",         r'=='),
            ("NEQ",        r'!='),
            ("LE",         r'<='),
            ("GE",         r'>='),
            ("ASSIGN",     r'='),
            ("LT",         r'<'),
            ("GT",         r'>'),
            ("PLUS",       r'\+'),
            ("MINUS",      r'-'),
            ("MUL",        r'\*'),
            ("DIV",        r'/'),
            ("LPAREN",     r'\('),
            ("RPAREN",     r'\)'),
            ("LBRACE",     r'\{'),
            ("RBRACE",     r'\}'),
            ("LBRACKET",   r'\['),
            ("RBRACKET",   r'\]'),
            ("COLON",      r':'),
            ("SEMICOLON",  r';'),
            ("COMMA",      r','),
            ("STRING_LITERAL", r'"[^"\n]*"'),
            ("NUMBER",     r'\b\d+\b'),
            ("IDENTIFIER", r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'),
            ("COMMENT",    r'//[^\n]*'),
            ("WHITESPACE", r'[ \t\n]+'),
        ]
        
        self.setup_ui()
        self.load_sample_code()
    
    def setup_ui(self):
        """Setup the GUI layout"""
        main_container = tk.Frame(self.root, bg='#2b2b2b')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        title = tk.Label(main_container, text="StarrLang", 
                        font=('Arial', 20, 'bold'), bg='#2b2b2b', fg='#00ff00')
        title.pack(pady=(0, 10))
        
        input_frame = tk.LabelFrame(main_container, text="Source Code", 
                                    font=('Arial', 12, 'bold'), 
                                    bg='#2b2b2b', fg='#ffffff', bd=2)
        input_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        self.code_input = scrolledtext.ScrolledText(input_frame, height=12, 
                                                    font=('Consolas', 11),
                                                    bg='#1e1e1e', fg='#ffffff',
                                                    insertbackground='white',
                                                    wrap=tk.WORD)
        self.code_input.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_frame = tk.Frame(main_container, bg='#2b2b2b')
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.compile_btn = tk.Button(button_frame, text="🔨 COMPILE", 
                                     command=self.compile_code,
                                     font=('Arial', 12, 'bold'),
                                     bg='#0d7377', fg='#ffffff',
                                     activebackground='#14a085',
                                     cursor='hand2', relief=tk.RAISED,
                                     bd=3, padx=20, pady=8)
        self.compile_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(button_frame, text="🗑️ CLEAR", 
                                   command=self.clear_all,
                                   font=('Arial', 12, 'bold'),
                                   bg='#c84b31', fg='#ffffff',
                                   activebackground='#e76f51',
                                   cursor='hand2', relief=tk.RAISED,
                                   bd=3, padx=20, pady=8)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Label(button_frame, text="Sample Code:", 
                font=('Arial', 10), bg='#2b2b2b', fg='#ffffff').pack(side=tk.LEFT, padx=(20, 5))
        
        self.sample_var = tk.StringVar()
        sample_dropdown = ttk.Combobox(button_frame, textvariable=self.sample_var,
                                      values=["Array Slicing", "String Slicing", 
                                             "For Loop", "Complex Example", 
                                             "Dead Code Test"],
                                      state='readonly', width=20)
        sample_dropdown.pack(side=tk.LEFT, padx=5)
        sample_dropdown.current(0)
        sample_dropdown.bind('<<ComboboxSelected>>', lambda e: self.load_sample_code())
        
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#2b2b2b', borderwidth=0)
        style.configure('TNotebook.Tab', background='#404040', foreground='#ffffff',
                       padding=[20, 10], font=('Arial', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#0d7377')],
                 foreground=[('selected', '#ffffff')])
        
        self.create_phase_tab("Tokens", "tokens")
        self.create_phase_tab("Syntax Tree", "syntax")
        self.create_phase_tab("Semantic Analysis", "semantic")
        self.create_phase_tab("Intermediate Code", "intermediate")
        self.create_phase_tab("Optimized Code", "optimized")
        self.create_phase_tab("Generated Code", "generated")
        self.create_phase_tab("Execution Output", "output")
        
        self.status_bar = tk.Label(self.root, text="Ready", 
                                   font=('Arial', 9), bg='#404040', 
                                   fg='#00ff00', anchor=tk.W, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_phase_tab(self, title, key):
        """Create a tab for a compilation phase"""
        frame = tk.Frame(self.notebook, bg='#2b2b2b')
        self.notebook.add(frame, text=title)
        
        text_widget = scrolledtext.ScrolledText(frame, font=('Consolas', 10),
                                                bg='#1e1e1e', fg='#ffffff',
                                                wrap=tk.WORD, state=tk.DISABLED)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        setattr(self, f"{key}_text", text_widget)
    
    def load_sample_code(self):
        """Load sample code based on selection"""
        samples = {
            "Array Slicing": '''array arr = {"A", "B", "C", "D"};
cout << arr[1:3];''',
            
            "String Slicing": '''string message = "Hello World";
cout << message[0:4];''',
            
            "For Loop": '''array names = {"Alice", "Bob", "Charlie"};
for (name in names) {
    cout << name;
}''',
            
            "Complex Example": '''array fruits = {"Apple", "Banana", "Cherry"};
string unused = "This will be optimized away";
string msg = "Fruits:";
cout << msg;
for (fruit in fruits) {
    cout << fruit;
}
cout << fruits[0:1];''',
            
            "Dead Code Test": '''string a = "First";
string b = a;
string c = b;
string unused = "Dead code";
cout << c;
array arr = {"X", "Y", "Z"};
cout << arr[0:2];'''
        }
        
        selected = self.sample_var.get()
        if selected in samples:
            self.code_input.delete(1.0, tk.END)
            self.code_input.insert(1.0, samples[selected])
    
    def clear_all(self):
        """Clear all text areas"""
        self.code_input.delete(1.0, tk.END)
        
        for phase in ['tokens', 'syntax', 'semantic', 'intermediate', 
                     'optimized', 'generated', 'output']:
            text_widget = getattr(self, f"{phase}_text")
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)
        
        self.update_status("Cleared", "green")
    
    def update_text(self, widget, content):
        """Update text widget content"""
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(1.0, content)
        widget.config(state=tk.DISABLED)
    
    def update_status(self, message, color="green"):
        """Update status bar"""
        colors = {"green": "#00ff00", "red": "#ff0000", "yellow": "#ffff00"}
        self.status_bar.config(text=message, fg=colors.get(color, "#00ff00"))
        self.root.update()
    
    def compile_code(self):
        """Run all compilation phases"""
        code = self.code_input.get(1.0, tk.END).strip()
        
        if not code:
            messagebox.showwarning("Warning", "Please enter source code!")
            return
        
        self.update_status("Compiling...", "yellow")
        self.compile_btn.config(state=tk.DISABLED)
        self.root.update()
        
        try:
            self.update_status("Phase 1: Lexical Analysis...", "yellow")
            lex = LexicalAnalysis(self.tokens)
            tokens = lex.lexer(code)
            
            tokens_output = "TOKENS:\n" + "="*50 + "\n"
            for i, (token_type, value) in enumerate(tokens, 1):
                tokens_output += f"{i:3}. {token_type:20} : {value}\n"
            tokens_output += f"\nTotal Tokens: {len(tokens)}"
            self.update_text(self.tokens_text, tokens_output)
            
            self.update_status("Phase 2: Syntax Analysis...", "yellow")
            syn = SyntaxAnalysis(tokens)
            syntax_tree = syn.parse_program()
            
            syntax_output = "ABSTRACT SYNTAX TREE:\n" + "="*50 + "\n"
            syntax_output += self.format_ast(syntax_tree)
            syntax_output += "\n✓ Syntax tree built successfully!"
            self.update_text(self.syntax_text, syntax_output)
            
            self.update_status("Phase 3: Semantic Analysis...", "yellow")
            sem = SemanticAnalysis()
            sem.analyze(syntax_tree)
            
            semantic_output = "SEMANTIC ANALYSIS:\n" + "="*50 + "\n"
            semantic_output += "✓ No semantic errors found!\n\n"
            semantic_output += "SYMBOL TABLE:\n" + "-"*50 + "\n"
            for var, var_type in sem.symbol_table.items():
                semantic_output += f"{var:20} : {var_type}\n"
            self.update_text(self.semantic_text, semantic_output)
            
            self.update_status("Phase 4: Intermediate Code Generation...", "yellow")
            ic = IntermediateCode()
            ic.generate(syntax_tree)
            
            intermediate_output = "INTERMEDIATE CODE:\n" + "="*50 + "\n"
            for i, instruction in enumerate(ic.get_code(), 1):
                intermediate_output += f"{i:3}. {instruction}\n"
            self.update_text(self.intermediate_text, intermediate_output)
            
            self.update_status("Phase 5: Code Optimization...", "yellow")
            optimizer = Optimizer(ic.get_code())
            optimized_code = optimizer.optimize()
            
            optimized_output = "OPTIMIZED CODE:\n" + "="*50 + "\n"
            optimized_output += f"Original: {len(ic.get_code())} instructions\n"
            optimized_output += f"Optimized: {len(optimized_code)} instructions\n"
            optimized_output += f"Reduction: {len(ic.get_code()) - len(optimized_code)} instructions\n\n"
            for i, instruction in enumerate(optimized_code, 1):
                optimized_output += f"{i:3}. {instruction}\n"
            self.update_text(self.optimized_text, optimized_output)
            
            self.update_status("Phase 6: Code Generation...", "yellow")
            codegen = CodeGenerator(optimized_code)
            python_code = codegen.generate()
            
            generated_output = "GENERATED PYTHON CODE:\n" + "="*50 + "\n"
            generated_output += python_code
            self.update_text(self.generated_text, generated_output)
            
            self.update_status("Phase 7: Execution...", "yellow")
            interpreter = Interpreter(optimized_code)
            
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                interpreter.execute()
                execution_output = captured_output.getvalue()
            finally:
                sys.stdout = old_stdout
            
            output_text = "EXECUTION OUTPUT:\n" + "="*50 + "\n"
            output_text += execution_output
            self.update_text(self.output_text, output_text)
            
            self.update_status("✓ Compilation Successful!", "green")
            messagebox.showinfo("Success", "Compilation completed successfully!")
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}"
            self.update_status(error_msg, "red")
            messagebox.showerror("Compilation Error", str(e))
            
            import traceback
            error_details = traceback.format_exc()
            current_tab = self.notebook.select()
            current_index = self.notebook.index(current_tab)
            
            phase_names = ['tokens', 'syntax', 'semantic', 'intermediate', 
                          'optimized', 'generated', 'output']
            if current_index < len(phase_names):
                error_text = f"ERROR in compilation:\n\n{error_details}"
                text_widget = getattr(self, f"{phase_names[current_index]}_text")
                self.update_text(text_widget, error_text)
        
        finally:
            self.compile_btn.config(state=tk.NORMAL)
    
    def format_ast(self, node, indent=0):
        """Format AST for display"""
        output = ""
        indent_str = "  " * indent
        
        node_type = type(node).__name__
        output += f"{indent_str}├─ {node_type}\n"
        
        if hasattr(node, 'statements'):
            for stmt in node.statements:
                output += self.format_ast(stmt, indent + 1)
        elif hasattr(node, 'name'):
            output += f"{indent_str}  └─ name: {node.name}\n"
            if hasattr(node, 'expression'):
                output += f"{indent_str}  └─ expression:\n"
                output += self.format_ast(node.expression, indent + 2)
        elif hasattr(node, 'value'):
            output += f"{indent_str}  └─ value: {node.value}\n"
        elif hasattr(node, 'elements'):
            output += f"{indent_str}  └─ elements:\n"
            for elem in node.elements:
                output += self.format_ast(elem, indent + 2)
        elif hasattr(node, 'body'):
            output += f"{indent_str}  └─ body:\n"
            for stmt in node.body:
                output += self.format_ast(stmt, indent + 2)
        
        return output


def main():
    root = tk.Tk()
    app = CompilerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()