def retiraEspacosVazios(lista, movimento):
    match movimento:
        case 'L': ## De baixo para cima
            j = 0
            for i in range(len(lista)):
                if lista[i] == 0:
                    j+=1
                elif lista[i-j] == 0:
                    lista[i-j] = lista[i]
                    lista[i] = 0
        case 'R': ## De cima para baixo
            j = 0
            for i in range(len(lista),0,-1):
                if lista[i-1] == 0:
                    j+=1
                elif lista[i+j-1] == 0:
                    lista[i+j-1] = lista[i-1]
                    lista[i-1] = 0


def somaPosicao(lista, movimento):
    retiraEspacosVazios(lista, movimento)
    match movimento:
        case 'L':
            i = 1
            while i < len(lista):
                if lista[i-1] != 0:
                    if lista[i-1] == lista[i]:
                        lista[i-1] = 3*lista[i]
                        lista[i] = 0
                i+=1
        case 'R':
            i = 1
            while i < len(lista):
                if lista[len(lista)-i] != 0:
                    if lista[len(lista)-1-i] == lista[len(lista)-i]:
                        lista[len(lista)-i] = 3*lista[len(lista)-i-1]
                        lista[len(lista)-i-1] = 0
                i+=1

    retiraEspacosVazios(lista, movimento)
    print(lista)

def deslizarMatriz(matriz, movimento):
    for i in range(4):
        somaPosicao(matriz[i], movimento)


matriz = [[1, 0, 0, 1],
          [1, 0, 0, 3],
          [1, 0, 0, 81],
          [0, 1, 9, 1]]

deslizarMatriz(matriz, 'R')





