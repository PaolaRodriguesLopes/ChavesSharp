from strings_with_arrows import *

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