from error import *
from saveNumbers import Number
from mappedTokens import MappedTokens
from runtimeResult import RTResult

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