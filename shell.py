# Esse documento ira ler o input no terminal
from run import Run
while True:
    text = input('ChavesSharp > ')
    result, error = Run.run('<stdin>',text)

    if error: print(error.as_string())
    elif result: print(result)