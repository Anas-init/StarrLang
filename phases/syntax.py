class Program:
    def __init__(self, statements):
        self.statements = statements

class Declaration:
    def __init__(self, typename, name, expression):
        self.typename = typename
        self.name = name
        self.expression = expression

class Assignment:
    def __init__(self, name, expression):
        self.name = name
        self.expression = expression

class Print:
    def __init__(self, printable):
        self.printable = printable

class Identifier:
    def __init__(self, name):
        self.name = name

class StringLiteral:
    def __init__(self, value):
        self.value = value

class IntLiteral:
    def __init__(self, value):
        self.value = int(value)

class ArrayLiteral:
    def __init__(self, elements):
        self.elements = elements

class SliceExpr:
    def __init__(self, name, start, end):
        self.name = name
        self.start = start
        self.end = end

class ForEachLoop:
    def __init__(self, var, iterable, body):
        self.var = var
        self.iterable = iterable
        self.body = body

class WhileLoop:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class BinaryOp:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class ArrayAccess:
    def __init__(self, name, index):
        self.name = name
        self.index = index

class FunctionCall:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class SyntaxAnalysis():
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def peek(self, offset=1):
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else None
    
    def match(self, *expected):
        token = self.current()
        if token and token[0] in expected:
            self.pos += 1
            return token
        return None

    def expect(self, expected):
        token = self.match(expected)
        if not token:
            raise SyntaxError(f"Expected {expected} at position {self.pos}")
        return token
    
    def parse_program(self):
        statements = []
        while self.current():
            statements.append(self.parse_statement())
        return Program(statements)
    
    def parse_statement(self):
        if self.current()[0] == "KEYWORD":
            if self.current()[1] == "for":
                return self.parse_for_loop()
            elif self.current()[1] == "while":
                return self.parse_while_loop()
            return self.parse_declaration()
        elif self.current()[0] == "COUT":
            return self.parse_print()
        else:
            return self.parse_assignment()
    
    def parse_declaration(self):
        typename = self.expect("KEYWORD")[1]  
        name = self.expect("IDENTIFIER")[1]
        self.expect("ASSIGN")
        expr = self.parse_expression()
        self.expect("SEMICOLON")
        return Declaration(typename, name, expr)
    
    def parse_assignment(self):
        name = self.expect("IDENTIFIER")[1]
        self.expect("ASSIGN")
        expr = self.parse_expression()
        self.expect("SEMICOLON")
        return Assignment(name, expr)

    def parse_print(self):
        self.expect("COUT")
        self.expect("SHL")
        printable = self.parse_printable()
        self.expect("SEMICOLON")
        return Print(printable)

    def parse_printable(self):
        if self.current()[0] == "IDENTIFIER":
            ident = self.expect("IDENTIFIER")[1]
            if self.match("LBRACKET"):
                start_expr = self.parse_expression()
                
                if self.match("COLON"):
                    end_expr = self.parse_expression()
                    self.expect("RBRACKET")
                    return SliceExpr(ident, start_expr, end_expr)
                else:
                    self.expect("RBRACKET")
                    return ArrayAccess(ident, start_expr)
            return Identifier(ident)
        elif self.current()[0] == "STRING_LITERAL":
            return StringLiteral(self.expect("STRING_LITERAL")[1])
        elif self.current()[0] == "NUMBER":
            return IntLiteral(self.expect("NUMBER")[1])
        else:
            return self.parse_expression()

    def parse_expression(self):
        left = self.parse_term()
        
        while self.current() and self.current()[0] == "PLUS":
            op = self.match("PLUS")[1]
            right = self.parse_term()
            left = BinaryOp(left, op, right)
        
        while self.current() and self.current()[0] == "MINUS":
            op = self.match("MINUS")[1]
            right = self.parse_term()
            left = BinaryOp(left, op, right)
        
        return left

    def parse_term(self):
        left = self.parse_factor()
        
        while self.current() and self.current()[0] in ("MUL", "DIV"):
            op = self.current()[1]
            self.pos += 1
            right = self.parse_factor()
            left = BinaryOp(left, op, right)
        
        return left

    def parse_factor(self):
        if self.current()[0] == "STRING_LITERAL":
            return StringLiteral(self.match("STRING_LITERAL")[1])
        elif self.current()[0] == "NUMBER":
            return IntLiteral(self.match("NUMBER")[1])
        elif self.current()[0] == "IDENTIFIER":
            name = self.match("IDENTIFIER")[1]
            
            if self.match("LPAREN"):
                args = []
                if self.current()[0] != "RPAREN":
                    args.append(self.parse_expression())
                    while self.match("COMMA"):
                        args.append(self.parse_expression())
                self.expect("RPAREN")
                return FunctionCall(name, args)
            
            elif self.match("LBRACKET"):
                index_expr = self.parse_expression()
                self.expect("RBRACKET")
                return ArrayAccess(name, index_expr)
            
            return Identifier(name)
        elif self.current()[0] == "LBRACE":
            return self.parse_array_literal()
        elif self.match("LPAREN"):
            expr = self.parse_expression()
            self.expect("RPAREN")
            return expr
        else:
            raise SyntaxError(f"Invalid expression at position {self.pos}")

    def parse_array_literal(self):
        elements = []
        self.expect("LBRACE")
        if self.current()[0] != "RBRACE":
            elements.append(self.parse_expression())
            while self.match("COMMA"):
                elements.append(self.parse_expression())
        self.expect("RBRACE")
        return ArrayLiteral(elements)

    def parse_for_loop(self):
        self.expect("KEYWORD")
        self.expect("LPAREN")
        loop_var = self.expect("IDENTIFIER")[1]
        self.expect("KEYWORD")
        iterable = self.expect("IDENTIFIER")[1]
        self.expect("RPAREN")
        self.expect("LBRACE")

        body = []
        while self.current() and self.current()[0] != "RBRACE":
            body.append(self.parse_statement())

        self.expect("RBRACE")
        return ForEachLoop(loop_var, iterable, body)

    def parse_while_loop(self):
        self.expect("KEYWORD")
        self.expect("LPAREN")
        condition = self.parse_condition()
        self.expect("RPAREN")
        self.expect("LBRACE")

        body = []
        while self.current() and self.current()[0] != "RBRACE":
            body.append(self.parse_statement())

        self.expect("RBRACE")
        return WhileLoop(condition, body)

    def parse_condition(self):
        left = self.parse_expression()
        
        if self.current() and self.current()[0] in ("LT", "GT", "LE", "GE", "EQ", "NEQ"):
            op = self.current()[1]
            self.pos += 1
            right = self.parse_expression()
            return BinaryOp(left, op, right)
        
        return left