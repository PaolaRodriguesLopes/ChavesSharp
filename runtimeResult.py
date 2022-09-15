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
