from lexer import Lexer
from context import Context
from saveVariableName import SymbolTable
from parser import Parser
from interpreter import Interpreter
from saveNumbers import Number

######################################### RUN ####################################################
# Adicionando configuracao para simbolos globais
global_symbol_table = SymbolTable()
# Caso o usuario digitar null, vai corresponder o mesmo que 0
global_symbol_table.set("null", Number(0))
global_symbol_table.set("false", Number(0))
global_symbol_table.set("true", Number(1))

# A funcao abaixo vai pegar o texto e executar no terminal
# Parametros passados é o nome do arquivo e o texto para que caso ocorra algum erro o usuário saiba de qual local ele esta retornando
class Run:
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