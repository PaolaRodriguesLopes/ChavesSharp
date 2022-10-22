
##################################### ARMAZENANDO NOME DE VARIAVEIS ################################
# Essa classe observa todos os nomes das variaveis criadas no sistema
class SymbolTable:

    # Adiciona todas variaveis na lista de simbolos e pai delas (ex: funcoes)
    # caso a funcao tenha terminado sua execucao o simbolo e removido
    # o parent e necessario par acaso a variavel for global, assim vai ser possivel acessar em qualuqer parte do sistema
	def __init__(self, parent=None):
		self.symbols = {}
		self.parent = parent

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