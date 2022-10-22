from error import *
from saveNumbers import Number
from mappedTokens import MappedTokens
from runtimeResult import RTResult
# from function import Function

from runtimeResult import RTResult
from context import *
from saveVariableName import *
from saveValue import *

######################################## INTERPRETADOR ###########################################
# Vai retornar o resultado da sintaxe
class Interpreter:

    def visit_FuncDefNode(self, node, context):
        res = RTResult()

        func_name = node.var_name_tok.value if node.var_name_tok else None
        body_node = node.body_node
        arg_names = [arg_name.value for arg_name in node.arg_name_toks]
        func_value = Function(func_name, body_node, arg_names).set_context(context).set_pos(node.pos_start, node.pos_end)
		
        if node.var_name_tok:
            context.symbol_table.set(func_name, func_value)

        return res.success(func_value)

    def visit_CallNode(self, node, context):
        res = RTResult()
        args = []

        value_to_call = res.register(self.visit(node.node_to_call, context))
        if res.error: return res
        value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

        for arg_node in node.arg_nodes:
            args.append(res.register(self.visit(arg_node, context)))
            if res.error: return res

        return_value = res.register(value_to_call.execute(args))
        if res.error: return res
        return res.success(return_value)

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
    def visit_StringNode(self, node, context):
        return RTResult().success(
			String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
		)    

    # Esse metodo determina qual operacao vai ser executada
    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left_node, context))
        if res.error: return res
        right = res.register(self.visit(node.right_node, context))
        if res.error: return res
        
        if node.op_tok.type == MappedTokens.TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_tok.type == MappedTokens.TT_MINUS:
            result, error = left.subbed_by(right)
        elif node.op_tok.type == MappedTokens.TT_MUL:
            result, error = left.multed_by(right)
        elif node.op_tok.type == MappedTokens.TT_DIV:
            result, error = left.dived_by(right)
        elif node.op_tok.type == MappedTokens.TT_POW:
            result, error = left.powed_by(right)
        elif node.op_tok.type == MappedTokens.TT_EE:
            result, error = left.get_comparison_eq(right)
        elif node.op_tok.type == MappedTokens.TT_NE:
            result, error = left.get_comparison_ne(right)
        elif node.op_tok.type == MappedTokens.TT_LT:
            result, error = left.get_comparison_lt(right)
        elif node.op_tok.type == MappedTokens.TT_GT:
            result, error = left.get_comparison_gt(right)
        elif node.op_tok.matches(MappedTokens.TT_KEYWORD, 'e'):
            result, error = left.anded_by(right)
        elif node.op_tok.matches(MappedTokens.TT_KEYWORD, 'ou'):
            result, error = left.ored_by(right)
        
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
        if node.op_tok.type == MappedTokens.TT_MINUS:
            number, error = number.multed_by(Number(-1))
        elif node.op_tok.matches(MappedTokens.TT_KEYWORD, 'negar'):
            number, error = number.notted()

        if error:
            return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

    def visit_IfNode(self, node, context):
        res = RTResult()

        # Visita cada par de condicoes do no de casos
        for condition, expr in node.cases:
            condition_value = res.register(self.visit(condition, context))
            if res.error: return res

            # Verifica se a condicao e verdadeira
            if condition_value.is_true():
                # Se a condicao e verdadeira a expressao e validada
                expr_value = res.register(self.visit(expr, context))
                if res.error: return res
                # Caso nao tenha erro retorna o valor com sucesso
                return res.success(expr_value)

        # Se a condicao nao for verdadeira procura pelo else
        if node.else_case:
            else_value = res.register(self.visit(node.else_case, context))
            if res.error: return res
            return res.success(else_value)
        
        return res.success(None)

    #
    def visit_ForNode(self, node, context):
        res = RTResult()

        start_value = res.register(self.visit(node.start_value_node, context))
        if res.error: return res

        end_value = res.register(self.visit(node.end_value_node, context))
        if res.error: return res
        
        # Caso tenha saltos definidos ele registra, se nao tiver assume com o valor 1
        if node.step_value_node:
            step_value = res.register(self.visit(node.step_value_node, context))
            if res.error: return res
        else:
            step_value = Number(1)

        i = start_value.value

        # Verifica se o numero e positivo ou negativo e seta a condicao de acordo
        if step_value.value >= 0:
            condition = lambda: i < end_value.value
        else:
            condition = lambda: i > end_value.value

        while condition():
            # Assinala a variavel para a condicao
            context.symbol_table.set(node.var_name_tok.value, Number(i))

            # Incrementa as execucoes
            i += step_value.value

            # Registra o corpo do for e executa
            res.register(self.visit(node.body_node, context))
            if res.error: return res

        return res.success(None)

    def visit_WhileNode(self, node, context):
        res = RTResult()

        while True:
            # Registra a condicao 
            condition = res.register(self.visit(node.condition_node, context))
            if res.error: return res
            
            # Se a condicao nao for verdadeira ele para a execucao
            if not condition.is_true(): break

            # Caso ainda esteja no looping continua executando a condicao
            res.register(self.visit(node.body_node, context))
            if res.error: return res

        return res.success(None)

class Function(Value):
	def __init__(self, name, body_node, arg_names):
		super().__init__()
		self.name = name or "<anonymous>"
		self.body_node = body_node
		self.arg_names = arg_names

	def execute(self, args):
		res = RTResult()
		interpreter = Interpreter()
		new_context = Context(self.name, self.context, self.pos_start)
		new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

		if len(args) > len(self.arg_names):
			return res.failure(RTError(
				self.pos_start, self.pos_end,
				f"{len(args) - len(self.arg_names)} muitos argumentos passados em '{self.name}'",
				self.context
			))
		
		if len(args) < len(self.arg_names):
			return res.failure(RTError(
				self.pos_start, self.pos_end,
				f"{len(self.arg_names) - len(args)} poucos argumentos passados em '{self.name}'",
				self.context
			))

		for i in range(len(args)):
			arg_name = self.arg_names[i]
			arg_value = args[i]
			arg_value.set_context(new_context)
			new_context.symbol_table.set(arg_name, arg_value)

		value = res.register(interpreter.visit(self.body_node, new_context))
		if res.error: return res
		return res.success(value)

	def copy(self):
		copy = Function(self.name, self.body_node, self.arg_names)
		copy.set_context(self.context)
		copy.set_pos(self.pos_start, self.pos_end)
		return copy

	def __repr__(self):
		return f"<function {self.name}>"

class String(Value):
	def __init__(self, value):
		super().__init__()
		self.value = value

	def added_to(self, other):
		if isinstance(other, String):
			return String(self.value + other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def multed_by(self, other):
		if isinstance(other, Number):
			return String(self.value * other.value).set_context(self.context), None
		else:
			return None, Value.illegal_operation(self, other)

	def is_true(self):
		return len(self.value) > 0

	def copy(self):
		copy = String(self.value)
		copy.set_pos(self.pos_start, self.pos_end)
		copy.set_context(self.context)
		return copy

	def __repr__(self):
		return f'"{self.value}"'
   