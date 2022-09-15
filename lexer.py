from token import Token 
from error import *
from position import Position
from mappedTokens import MappedTokens


######################################## ANALISE LEXICA ##########################################
# Analise lexica

class Lexer:
    # Acompanha a posicao atual, a posicao do caractere e avanca para o proximo
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    # Vai avancar para o proximo caractere no texto
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    # Mapeia os tokens digitados no terminal
    def make_tokens(self):
        tokens = []

        # percorre todo o texto
        while self.current_char != None:
            # ignora espacos e tabs
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in MappedTokens.DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in MappedTokens.LETTERS:
                tokens.append(self.binary_expression())
            elif self.current_char == '(':
                tokens.append(Token(MappedTokens.TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(MappedTokens.TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        # Antes de finalizar é preciso adicionar mais um token informando que a operacao acabou
        tokens.append(Token(MappedTokens.TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in MappedTokens.DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char

            self.advance()

        if dot_count == 0:
            return Token(MappedTokens.TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(MappedTokens.TT_FLOAT, float(num_str), pos_start, self.pos)

    def binary_expression(self):
        let_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in MappedTokens.LETTERS_DIGITS + '_':
            let_str += self.current_char
            self.advance()

        if let_str == 'mais':
            return Token(MappedTokens.TT_PLUS, pos_start=self.pos)
        elif let_str == 'menos':
            return Token(MappedTokens.TT_MINUS, pos_start=self.pos)
        elif let_str == 'vezes':
            return Token(MappedTokens.TT_MUL, pos_start=self.pos)
        elif let_str == 'dividido':
            return Token(MappedTokens.TT_DIV, pos_start=self.pos)
        elif let_str == 'elevado':
            return Token(MappedTokens.TT_POW, pos_start=self.pos)
        elif let_str == 'recebe':
            return Token(MappedTokens.TT_EQ, pos_start=self.pos)
        elif let_str == 'diferente':            
            return Token(MappedTokens.TT_NE, pos_start=self.pos)
        elif let_str == 'igual':
            return Token(MappedTokens.TT_EE, pos_start=pos_start, pos_end=self.pos)
        elif let_str == 'menor':
            return Token(MappedTokens.TT_LT, pos_start=self.pos)
        elif let_str == 'maior':
            return Token(MappedTokens.TT_GT, pos_start=self.pos)
        else:
            tok_type = MappedTokens.TT_KEYWORD if let_str in MappedTokens.KEYWORDS else MappedTokens.TT_IDENTIFIER
            return Token(tok_type, let_str, pos_start, self.pos)