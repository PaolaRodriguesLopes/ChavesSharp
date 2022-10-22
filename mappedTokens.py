import string

class MappedTokens:
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
    TT_EE = 'IGUAL'
    TT_NE = 'DIFERENTE'
    TT_LT = 'MENOR'
    TT_GT = 'MAIOR'
    TT_EQ = 'RECEBE'
    TT_COMMA = 'VIRGULA'
    TT_FUNC = 'FUNCAO'

    KEYWORDS = [
        'tamarindo',
        'e',
        'ou',
        'negar',
        'issoIssoIsso',    
        'aiQueBurro',
        'taBomNaoSeIrrite',
        'evitarFadiga',
        'ate',
        'piPiPi',
        'passos',
        'voltaOCaoArrependido',
        'zas',
    ]