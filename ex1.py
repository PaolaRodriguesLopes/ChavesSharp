from run import Run

if __name__ == "__main__":
    with open('./codeEx1.txt') as file:    
        linhas = file.readlines()
    for linha in linhas:
        text = linha.strip()
        result, error = Run.run('<stdin>',text)

        if error: print(error.as_string())
        elif result: print(result)

pass