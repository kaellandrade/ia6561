lista = [1,0,1,0]

def retiraEspacosVazios(lista):
    j = 0
    for i in range(len(lista)):
        if lista[i] == 0:
            j+=1
        elif lista[i-j] == 0:
            lista[i-j] = lista[i]
            lista[i] = 0

def somaPosicao(lista):
    retiraEspacosVazios(lista)
    i = 1
    while i < len(lista):
        if lista[i-1] == 1:
            if lista[i-1] == lista[i]:
                lista[i-1] = 3
                lista[i] = 0
        i+=1
    retiraEspacosVazios(lista)
    print(lista)

somaPosicao(lista)
