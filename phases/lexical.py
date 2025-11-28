import re

class LexicalAnalysis():
    def __init__(self,tokens):
        self.token_specs = tokens

    def lexer(self, code):
        tokens = []
        combined_regex = "|".join(f"(?P<{t}>{r})" for t, r in self.token_specs)
        pattern = re.compile(combined_regex)
        
        for match in pattern.finditer(code):
            token_type = match.lastgroup
            value = match.group(token_type)
            if token_type in ("WHITESPACE", "COMMENT"):
                continue
            tokens.append((token_type, value))
        return tokens

