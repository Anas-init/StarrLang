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

class ArrayLiteral:
    def __init__(self, elements):
        self.elements = elements

class SliceExpr:
    def __init__(self, name, start, end):
        self.name = name
        self.start = int(start)
        self.end = int(end)

class ForEachLoop:
    def __init__(self, var, iterable, body):
        self.var = var
        self.iterable = iterable
        self.body = body

class SyntaxAnalysis():

    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
    
    def current(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
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
                start = self.expect("NUMBER")[1]
                self.expect("COLON")
                end = self.expect("NUMBER")[1]
                self.expect("RBRACKET")
                return SliceExpr(ident, start, end)
            return Identifier(ident)
        elif self.current()[0] == "STRING_LITERAL":
            return StringLiteral(self.expect("STRING_LITERAL")[1])
        else:
            raise SyntaxError("Invalid print expression")

    def parse_expression(self):
        if self.current()[0] == "STRING_LITERAL":
            return StringLiteral(self.match("STRING_LITERAL")[1])
        elif self.current()[0] == "IDENTIFIER":
            return Identifier(self.match("IDENTIFIER")[1])
        elif self.current()[0] == "LBRACE":
            return self.parse_array_literal()
        else:
            raise SyntaxError("Invalid expression")

    def parse_array_literal(self):
        elements = []
        self.expect("LBRACE")
        elements.append(self.parse_expression())
        while self.match("COMMA"):
            elements.append(self.parse_expression())
        self.expect("RBRACE")
        return ArrayLiteral(elements)

    def parse_for_loop(self):
        self.expect("KEYWORD")    # for
        self.expect("LPAREN")
        loop_var = self.expect("IDENTIFIER")[1]
        self.expect("KEYWORD")    # in
        iterable = self.expect("IDENTIFIER")[1]
        self.expect("RPAREN")
        self.expect("LBRACE")

        body = []
        while self.current() and self.current()[0] != "RBRACE":
            body.append(self.parse_statement())

        self.expect("RBRACE")
        return ForEachLoop(loop_var, iterable, body)