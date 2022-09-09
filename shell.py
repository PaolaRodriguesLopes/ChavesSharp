# Esse documento ira ler o input no terminal
import chavesSharpBasic
while True:
    text = input('ChavesSharp > ')
    result, error = chavesSharpBasic.run('<stdin>',text)
    if error: print(error.as_string())
    else: print(result)