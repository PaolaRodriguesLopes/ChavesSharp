
import chavesSharpBasic

if __name__ == "__main__":
    with open('./codigo.txt') as file:    
        linhas = file.readlines()
    for linha in linhas:
        text = linha.strip()
        # result = chavesSharpBasic.run('<stdin>',text)
        # print(result.var_name_tok)
        lexer = chavesSharpBasic.Lexer('<stdin>', text)
        tokens, error = lexer.make_tokens()
        print(tokens)

pass