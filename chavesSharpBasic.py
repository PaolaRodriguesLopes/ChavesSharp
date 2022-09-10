from strings_with_arrows import *

# Constantes
DIGITS = '0123456789'
LETTERS = 'abcdefghijklmnopqrstuvwxyz'

######################################## TOKENS ###############################################
# Criando tokens
TT_INT = 'PAGUEALUGUEL'
TT_FLOAT = 'GENTALHAGENTALHA'
TT_PLUS = 'MAIS'
TT_MINUS = 'MENOS'
TT_MUL = 'VEZES'
TT_DIV = 'DIVIDIDO'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type = type_
        self.value = value

        # Esse pedaco do codigo serve para identificar possiveis erros
        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()

        if pos_end:
            self.pos_end = pos_end

        # Ira printar no terminal
    # Se tem algum valor, vai printar o tipo e valor junto, se nao vai retornar apenas o valor
    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

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
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char in LETTERS:
                tokens.append(self.binary_expression())
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start=self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start=self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        # Antes de finalizar é preciso adicionar mais um token informando que a operacao acabou
        tokens.append(Token(TT_EOF, pos_start=self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char

            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

    def binary_expression(self):
        let_str = ''
        pos_start = self.pos.copy()

        while self.current_char != None and self.current_char in LETTERS:
            let_str += self.current_char
            self.advance()

        if let_str == 'mais':
            return Token(TT_PLUS, pos_start=self.pos)
        elif let_str == 'menos':
            return Token(TT_MINUS, pos_start=self.pos)
        elif let_str == 'vezes':
            return Token(TT_MUL, pos_start=self.pos)
        elif let_str == 'dividido':
            return Token(TT_DIV, pos_start=self.pos)

################################################# TRATAMENTO DE ERROS ##################################
# Tratando erros


class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    # Formata o erro para mostrar no terminal
    def as_string(self):
        result = f'{self.error_name}: {self.details}\n'
        result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
        return result

# Retorna todos os caracteres ilegais que não foram tratados


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, 'Illegal Character', details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

###################################### POSICAO ###############################################
# Retorna a posicao


class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt

    # O metodo incrementa o index e a coluna
    def advance(self, current_char=None):
        self.idx += 1
        self.col += 1

        # Caso tenha uma nova linha, ele zera coluna e incrementa a linha
        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self

    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

############################################### NOS ###########################################
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

# Criando regra para expressao de calculos dentro do parenteses
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

############################################## PARSER ############################################


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    # Recebe um resultado de passagem ou um no e verifica se ocorreu algum erro
    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node

        return res

    # Metodo de sucesso vai apenas atribuir o no
    def success(self, node):
        self.node = node
        return self

    # Metodo de falha apenas vai determinar o erro
    def failure(self, error):
        self.error = error
        return self
# Parser
# Ira converter os tokens para uma syntax abstrata
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self, ):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    # Verifica se não tem erros e tambem verifica se nao e o final do arquivo
    def parse(self):
        res = self.expr()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Expected 'mais', 'menos', 'vezes' or 'dividido'"
            ))
        return res

# Validando gramatica
    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected ')'"
                ))

        return res.failure(InvalidSyntaxError(
            tok.pos_start, tok.pos_end,
            "Expected pague_o_aluguel or gentalha_gentalha"
        ))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

# Validadando operacoes

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)

######################################### RUN ####################################################

# A funcao abaixo vai pegar o texto e executar no terminal
# Parametros passados é o nome do arquivo e o texto para que caso ocorra algum erro o usuário saiba de qual local ele esta retornando

def run(fn, text):
    # Gerando os tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Gerando a sintaxe abstrata
    parser = Parser(tokens)
    ast = parser.parse()

    # Remove o no da arvore e tambem remove o erro
    return ast.node, ast.error
