from error import *
from node import *
from mappedTokens import MappedTokens

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
        if not res.error and self.current_tok.type != MappedTokens.TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.current_tok.pos_start, self.current_tok.pos_end,
                "Esperado 'mais', 'menos', 'vezes' ou 'dividido'"
            ))
        return res

# Validando gramatica
    def atom(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (MappedTokens.TT_INT, MappedTokens.TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        # Verifica se o tipo de token e um identificador, se sim retorna um novo no
        elif tok.type == MappedTokens.TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == MappedTokens.TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type == MappedTokens.TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Esperado ')'"
				))

        elif tok.matches(MappedTokens.TT_KEYWORD, 'issoIssoIsso'):
            if_expr = res.register(self.if_expr())
            if res.error: return res
            return res.success(if_expr)

        elif tok.matches(MappedTokens.TT_KEYWORD, 'evitarFadiga'):
            for_expr = res.register(self.for_expr())
            if res.error: return res
            return res.success(for_expr)
        
        elif tok.matches(MappedTokens.TT_KEYWORD, 'voltaOCaoArrependido'):
            while_expr = res.register(self.while_expr())
            if res.error: return res
            return res.success(while_expr)
        
        return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Esperado pague_o_aluguel, gentalha_gentalha, identificador, 'mais', 'menos' or '('"
		))

    def if_expr(self):
        res = ParseResult()
        cases = []
        else_case = None

        # Primeiro procura-se a keyword correspondente ao if
        if not self.current_tok.matches(MappedTokens.TT_KEYWORD, 'issoIssoIsso'):
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Esperado 'issoIssoIsso'"
			))
        res.register_advancement()
        self.advance()
        
        # Grava a conficao do primeiro if
        condition = res.register(self.expr())
        if res.error: return res

        # Procura o corpo do if
        if not self.current_tok.matches(MappedTokens.TT_KEYWORD, 'zas'):
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Esperado 'zas'"
			))

        res.register_advancement()
        self.advance()

        # Registra o corpo do if com suas acoes
        expr = res.register(self.expr())
        if res.error: return res

        # Adiciona nos casos a condicao e a expressao
        cases.append((condition, expr))

        # Procura todos os else if
        while self.current_tok.matches(MappedTokens.TT_KEYWORD, 'aiQueBurro'):
            res.register_advancement()
            self.advance()

            # Grava a condicao
            condition = res.register(self.expr())
            if res.error: return res

            # Procura o corpo
            if not self.current_tok.matches(MappedTokens.TT_KEYWORD, 'zas'):
                return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					f"Esperado 'zas'"
				))
            res.register_advancement()
            self.advance()

            # Registra o corpo do else if com suas acoes
            expr = res.register(self.expr())
            if res.error: return res

            # Adiciona nos casos a condicao e a expressao
            cases.append((condition, expr))
        
        # Procura pelo else
        if self.current_tok.matches(MappedTokens.TT_KEYWORD, 'taBomNaoSeIrrite'):
            res.register_advancement()
            self.advance()
            
            else_case = res.register(self.expr())
            if res.error: return res
        
        return res.success(IfNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()
        
        # Procura pela keyword do for
        if not self.current_tok.matches(MappedTokens.TT_KEYWORD, 'evitarFadiga'):
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Esperado 'evitarFadiga'"
			))
        
        res.register_advancement()
        self.advance()
        
        # procuta um identificador de nome de variaveis
        if self.current_tok.type != MappedTokens.TT_IDENTIFIER:
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Esperado um identificador"
			))
        
        # adiciona o nome da variavel
        var_name = self.current_tok
        res.register_advancement()
        self.advance()
        
        # Progura um operado de igual para informar o inicio
        if self.current_tok.type != MappedTokens.TT_EQ:
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Esperado 'igual'"
			))

        res.register_advancement()
        self.advance()

        # Adiciona o comeco
        start_value = res.register(self.expr())
        if res.error: return res

        # Procura o operador de ate para saber quantas execucoes
        if not self.current_tok.matches(MappedTokens.TT_KEYWORD, 'ate'):
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Esperado 'ate'"
			))

        res.register_advancement()
        self.advance()

        # Adiciona a quantidade de iterações
        end_value = res.register(self.expr())
        if res.error: return res

        # Procura o identificador de saltos e atribui quantos salto a cada iteracao
        if self.current_tok.matches(MappedTokens.TT_KEYWORD, 'passos'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error: return res
        else:
            step_value = None

        # Procura o inicio do corpo
        if not self.current_tok.matches(MappedTokens.TT_KEYWORD, 'zas'):
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Esperado 'zas'"
			))

        res.register_advancement()
        self.advance()

        # Adiciona o corpo nas repeticoes
        body = res.register(self.expr())
        if res.error: return res

        return res.success(ForNode(var_name, start_value, end_value, step_value, body))

    def while_expr(self):
        res = ParseResult()

        # Procura a keyword do while
        if not self.current_tok.matches(MappedTokens.TT_KEYWORD, 'voltaOCaoArrependido'):
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Esperado 'voltaOCaoArrependido'"
			))

        res.register_advancement()
        self.advance()

        # Adiciona a condicao
        condition = res.register(self.expr())
        if res.error: return res

        # Procura o corpo da keyword
        if not self.current_tok.matches(MappedTokens.TT_KEYWORD, 'zas'):
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				f"Expected 'zas'"
			))

        res.register_advancement()
        self.advance()

        # Adiciona o corpo na execucao
        body = res.register(self.expr())
        if res.error: return res

        return res.success(WhileNode(condition, body))

    
    def power(self):
        return self.bin_op(self.atom, (MappedTokens.TT_POW, ), self.factor)


    def factor(self):
        res = ParseResult()
        tok = self.current_tok
        
        if tok.type in (MappedTokens.TT_PLUS, MappedTokens.TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))
        
        return self.power()
    
    # Termos que tem maior prioridade 
    def term(self):
        return self.bin_op(self.factor, (MappedTokens.TT_MUL, MappedTokens.TT_DIV))

    # Operadores com menor prioridade
    def arith_expr(self):
        return self.bin_op(self.term, (MappedTokens.TT_PLUS, MappedTokens.TT_MINUS))

    # Compara os operadores logicos
    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(MappedTokens.TT_KEYWORD, 'negar'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            node = res.register(self.comp_expr())
            if res.error: return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(self.bin_op(self.arith_expr, (MappedTokens.TT_EE, MappedTokens.TT_NE, MappedTokens.TT_LT, MappedTokens.TT_GT)))

        # Mensagem de erro para caso nao seja um operador logico
        if res.error:
            return res.failure(InvalidSyntaxError(
				self.current_tok.pos_start, self.current_tok.pos_end,
				"Esperado pague_o_aluguel, gentalha_gentalha, identificador, 'mais', 'menos', '(' ou 'negar'"
			))
        return res.success(node)

    def expr(self):
        res = ParseResult()
        
        # Verifica o tipo de chave
        if self.current_tok.matches(MappedTokens.TT_KEYWORD, 'tamarindo'):
            res.register_advancement()
            self.advance()

            # Se o tipo de token nao for diferente do identificador, ele cria uma falha
            if self.current_tok.type != MappedTokens.TT_IDENTIFIER:
                return res.failure(InvalidSyntaxError(
					self.current_tok.pos_start, self.current_tok.pos_end,
					"Esperado um identificador"
				))
            
            # Caso o usuario esteja tentando criar uma variavel, aqui e onde e atribuido o nome
            var_name = self.current_tok
            res.register_advancement()
            self.advance()
            
            # O proximo token precisa ser o token de atribuicao de valor 
            if self.current_tok.type != MappedTokens.TT_EQ:
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

        # Para criar o no e preciso pesquisar primeiro se tem uma comparacao na expressao
        node = res.register(self.bin_op(self.comp_expr, ((MappedTokens.TT_KEYWORD, 'e'), (MappedTokens.TT_KEYWORD, 'ou'))))
        
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
        
        # Permite operadores logicos e aritmeticos
        while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        
        return res.success(left)