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