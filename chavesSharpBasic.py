# Constantes 
DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyz'

# Criando tokens 
TT_INT		= 'PAGUE_O_ALUGUEL'
TT_FLOAT    = 'GENTALHA_GENTALHA'
TT_PLUS     = 'MAIS'
TT_MINUS    = 'MENOS'
TT_MUL      = 'VEZES'
TT_DIV      = 'DIVIDO'
TT_LPAREN   = 'LPAREN'
TT_RPAREN   = 'RPAREN'

class Token:
    def __init__(self, type_, value=None):
        self.type = type_
        self.value = value
    
    # Ira printar no terminal 
    # Se tem algum valor, vai printar o tipo e valor junto, se nao vai retornar apenas o valor
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

# A funcao abaixo vai pegar o texto e executar no terminal 
# Parametros passados é o nome do arquivo e o texto para que caso ocorra algum erro o usuário saiba de qual local ele esta retornando
def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()

    return tokens, error

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
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.binary_expression())
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
    
    def binary_expression(self):
        let_str = ''
        while self.current_char != None and self.current_char in LETTERS:
            let_str += self.current_char
            self.advance()

        if let_str == 'mais':
            return Token(TT_PLUS)
        elif let_str == 'menos':
            return Token(TT_MINUS)
        elif let_str == 'vezes':
            return Token(TT_MUL)
        elif let_str == 'dividido':
            return Token(TT_DIV)

# Tratando erros 
class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    # Formata o erro para mostrar no terminal
    def as_string(self):
        result  = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        return result

# Retorna todos os caracteres ilegais que não foram tratados
class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)

# Retorna a posicao
class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    # O metodo incrementa o index e a coluna
    def advance(self, current_char):
        self.idx += 1
        self.col += 1

        # Caso tenha uma nova linha, ele zera coluna e incrementa a linha
        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

# Nos
# Definindo o tipo numerico de no, apenas vai recer um int ou um float  
class NumberNode:
	def __init__(self, tok):
		self.tok = tok

    # Retorna a representacao do token
	def __repr__(self):
		return f'{self.tok}'

# Node para operacoes matematicas
# Precisa do node da esquerda e da direita e o token operador
class BinOpNode:
	def __init__(self, left_node, op_tok, right_node):
		self.left_node = left_node
		self.op_tok = op_tok
		self.right_node = right_node

	def __repr__(self):
		return f'({self.left_node}, {self.op_tok}, {self.right_node})'

class UnaryOpNode:
	def __init__(self, op_tok, node):
		self.op_tok = op_tok
		self.node = node

	def __repr__(self):
		return f'({self.op_tok}, {self.node})'