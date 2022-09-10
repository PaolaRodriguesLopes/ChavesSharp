from strings_with_arrows import *
import string

# Constantes
DIGITS = '0123456789'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS 

######################################## TOKENS ###############################################
# Criando tokens
TT_INT = 'PAGUE_O_ALUGUEL'
TT_FLOAT = 'GENTALHA_GENTALHA'
TT_IDENTIFIER	= 'IDENTIFIER'
TT_KEYWORD		= 'KEYWORD'
TT_PLUS = 'MAIS'
TT_MINUS = 'MENOS'
TT_MUL = 'VEZES'
TT_DIV = 'DIVIDIDO'
TT_POW = 'ELEVADO'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'
TT_EQ = 'RECEBE'

KEYWORDS = [
	'tamarindo'
]

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

    # Verifica se o tipo e valor sao os mesmos
    def matches(self, type_, value):
        return self.type == type_ and self.value == value

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

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
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
        elif let_str == 'elevado':
            return Token(TT_POW, pos_start=self.pos)
        elif let_str == 'recebe':
            return Token(TT_EQ, pos_start=self.pos)
        else:
            tok_type = TT_KEYWORD if let_str in KEYWORDS else TT_IDENTIFIER
            return Token(tok_type, let_str, pos_start, self.pos)

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
        super().__init__(pos_start, pos_end, 'Caracter invalido', details)

# Retorna o erro de sintaxe
class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details=''):
        super().__init__(pos_start, pos_end, 'Sintaxe invalida', details)

# Erros de execucao do interpretador 
class RTError(Error):
	def __init__(self, pos_start, pos_end, details, context):
		super().__init__(pos_start, pos_end, 'Erro de execução', details)
		self.context = context

	def as_string(self):
		result  = self.generate_traceback()
		result += f'{self.error_name}: {self.details}'
		result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
		return result

	def generate_traceback(self):
		result = ''
		pos = self.pos_start
		ctx = self.context

		while ctx:
			result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
			pos = ctx.parent_entry_pos
			ctx = ctx.parent

		return 'Traceback (most recent call last):\n' + result

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
        self.pos_start = self.tok.pos_start
        self.pos_end = self.tok.pos_end

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
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end

    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.right_node})'

# Criando regra para expressao de calculos dentro do parenteses
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end

    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

# Criando um no com o nome da variavel
class VarAccessNode:
	def __init__(self, var_name_tok):
		self.var_name_tok = var_name_tok

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.var_name_tok.pos_end

# Criando um no com o nome da variavel e atribuindo valor 
class VarAssignNode:
	def __init__(self, var_name_tok, value_node):
		self.var_name_tok = var_name_tok
		self.value_node = value_node

		self.pos_start = self.var_name_tok.pos_start
		self.pos_end = self.value_node.pos_end

############################################## PARSER ############################################
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.advance_count = 0

    # Recebe um resultado de passagem ou um no e verifica se ocorreu algum erro
    def register(self, res):
        self.advance_count += res.advance_count
        if res.error: self.error = res.error
        return res.node

    def register_advancement(self):
        self.advance_count += 1

    # Metodo de sucesso vai apenas atribuir o no
    def success(self, node):
        self.node = node
        return self

    # Metodo de falha apenas vai determinar o erro
    def failure(self, error):
        if not self.error or self.advance_count == 0:
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
                "Esperado 'mais', 'menos', 'vezes' ou 'dividido'"
            ))
        return res

# Validando gramatica
    def atom(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        # Verifica se o tipo de token e um identificador, se sim retorna um novo no
        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Esperado ')'"
				))
        
        return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Esperado pague_o_aluguel, gentalha_gentalha, identificador, 'mais', 'menos' or '('"
		))
    
    def power(self):
        return self.bin_op(self.atom, (TT_POW, ), self.factor)


    def factor(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))
        
        return self.power()
    
    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        res = ParseResult()
        
        # Verifica o tipo de chave
        if self.current_tok.matches(TT_KEYWORD, 'tamarindo'):
            res.register_advancement()
            self.advance()

            # Se o tipo de token nao for diferente do identificador, ele cria uma falha
            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Esperado um identificador"
				))
            
            # Caso o usuario esteja tentando criar uma variavel, aqui e onde e atribuido o nome
            var_name = self.current_tok
            res.register_advancement()
            self.advance()
            
            # O proximo token precisa ser o token de atribuicao de valor 
            if self.current_tok.type != TT_EQ:
                return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Esperado '->'"
				))

            # A nova expressao e atribuida para a variavel que foi criada
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            return res.success(VarAssignNode(var_name, expr))

        node = res.register(self.bin_op(self.term, (TT_PLUS, TT_MINUS)))
        
        if res.error:
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Esperado 'tamarindo', pague_o_aluguel, gentalha_gentalha, identificador, 'mais', 'menos' or '('"
			))
        return res.success(node)

# Validadando operacoes

    def bin_op(self, func_a, ops, func_b=None):
        if func_b == None:
            func_b = func_a

        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res
        
        while self.current_tok.type in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        
        return res.success(left)

######################################## INTERPRETADOR ###########################################
# Vai retornar o resultado da sintaxe
class Interpreter:

    def visit_VarAccessNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = context.symbol_table.get(var_name)
        if not value:
            return res.failure(RTError(
				node.pos_start, node.pos_end,
				f"'{var_name}' não está definido",
				context
			))
        
        value = value.copy().set_pos(node.pos_start, node.pos_end)
        return res.success(value)
    
    def visit_VarAssignNode(self, node, context):
        res = RTResult()
        var_name = node.var_name_tok.value
        value = res.register(self.visit(node.value_node, context))
        if res.error: return res

        context.symbol_table.set(var_name, value)
        return res.success(value)
    
    def visit(self, node, context):
        # O metodo vai criar uma string chamada visit number node
        method_name = f'visit_{type(node).__name__}'
        # A partir do nome, vai ser chamado o metodo de acordo
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    # Mensagem para caso o metodo do no nao esteja definido
    def no_visit_method(self, node, context):
        raise Exception(f'No visit_{type(node).__name__} method defined')

	############### TIPOS DE METODO QUE DEFINE OPERACOES ####################

    # Retorna sucesso, pois não tem nenhuma operacao envolvida, é apenas numeros
    def visit_NumberNode(self, node, context):
        return RTResult().success(
			Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)    

    # Esse metodo determina qual operacao vai ser executada
    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res
        
        if node.op_tok.type == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == TT_POW:
            result, error = left.powed_by(right)
        
        if error:
            return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    # Verica operacoes unitarias, como por exemplo -4 ...
    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res
        error = None

        # Caso o operador e menos, multiplica por menos 1 para nega-lo
        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_by(Number(-1))
        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

################################### ARMAZENANDO VALORES #####################################
# Essa classe serve apenas para armazenas os valores e em  seguida opera-los com outros numeros

class Number:
	def __init__(self, value):
		self.value = value
		self.set_pos()
		self.set_context()

    # Gravando a posicao para que caso tenha alguma divisao por 0 o erro vai ser exibido corretamente
	def set_pos(self, pos_start=None, pos_end=None):
		self.pos_start = pos_start
		self.pos_end = pos_end
		return self

	def set_context(self, context=None):
		self.context = context
		return self

    # As operacoes abaixo fazem a validacao se esta sendo feitas as operacoes com outros numeros, ou seja, pegando outra posicao
    # Todos retornan um numero e adicionam ao um outro valor
	def added_to(self, other):
		if isinstance(other, Number):
			return Number(self.value + other.value).set_context(self.context), None

	def subbed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value - other.value).set_context(self.context), None

	def multed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value * other.value).set_context(self.context), None

	def dived_by(self, other):
		if isinstance(other, Number):
			if other.value == 0:
				return None, RTError(
					other.pos_start, other.pos_end,
					'Divisão por 0',
					self.context
				)

			return Number(self.value / other.value).set_context(self.context), None

	def powed_by(self, other):
		if isinstance(other, Number):
			return Number(self.value ** other.value).set_context(self.context), None    

	def copy(self):
		copy = Number(self.value)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy

	def __repr__(self):
		return str(self.value)

##################################### ARMAZENANDO NOME DE VARIAVEIS ################################
# Essa classe observa todos os nomes das variaveis criadas no sistema
class SymbolTable:

    # Adiciona todas variaveis na lista de simbolos e pai delas (ex: funcoes)
    # caso a funcao tenha terminado sua execucao o simbolo e removido
    # o parent e necessario par acaso a variavel for global, assim vai ser possivel acessar em qualuqer parte do sistema
	def __init__(self):
		self.symbols = {}
		self.parent = None

	def get(self, name):
		value = self.symbols.get(name, None)
        # Verifica se a variavel est ano dicionario
        # verifica se ela e parent, se sim vai ser considerado uma variavel global
		if value == None and self.parent:
			return self.parent.get(name)
		return value

    # Adicionando variavel para o dicionario
	def set(self, name, value):
		self.symbols[name] = value

	def remove(self, name):
		del self.symbols[name]

####################################### RESULTADOS DE EXECUCAO ##############################################
# Essa classe acompanha o resultado atual e o erro 
class RTResult:
	def __init__(self):
		self.value = None
		self.error = None

    # Veridica se ocorreu algum erro, se sim retorna o erro
	def register(self, res):
		if res.error: self.error = res.error
		return res.value

    # Sucesso atualiza o valor 
	def success(self, value):
		self.value = value
		return self

    # A parte de falha atualiza o erro para a mensagem
	def failure(self, error):
		self.error = error
		return self


######################################## CONTEXTO ERRO ########################################
# Atualiza o erro em tempo de execucao e mostra o contexto do erro
class Context:
	def __init__(self, display_name, parent=None, parent_entry_pos=None):
		self.display_name = display_name
		self.parent = parent
		self.parent_entry_pos = parent_entry_pos
		self.symbol_table = None

######################################### RUN ####################################################
# Adicionando configuracao para simbolos globais
global_symbol_table = SymbolTable()
# Caso o usuario digitar null, vai corresponder o mesmo que 0
global_symbol_table.set("null", Number(0))

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
    if ast.error: return None, ast.error

    # Executando o programa ja com os resultados
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    # Remove o no da arvore e tambem remove o erro
    # return ast.node, ast.error
    return result.value, result.error
