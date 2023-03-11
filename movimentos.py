

import numpy as np

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
    # TODO: a função está juntando mais de duas peças numa mesma ação -> contra as regras
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



def transporMatriz(matriz):
    return [list(coluna) for coluna in zip(*matriz)]


def deslizarMatriz(matriz, movimento):
    if movimento == 'R' or movimento == 'L':
        for i in range(4):
            somaPosicao(matriz[i], movimento)
        for i in range(4):
            print(matriz[i])
    else:
        # OBS: PERCEBA QUE O MOVIMENTO DE UP É A MESMA COISA QUE O DE LEFT, E O MOVIMENTO DE DOWN A MESMA COISA
        #     QUE O MOVIMENTO DE RIGHT, ISSO QUANDO A MATRIZ É TRANSPOSTA
        matriz_transposta = transporMatriz(matriz)
        for i in range(4):
            if movimento == 'U':
                somaPosicao(matriz_transposta[i], 'L')
            else:
                somaPosicao(matriz_transposta[i], 'R')
        matriz_movimentada = transporMatriz(matriz_transposta)
        for i in range(4):
            print(matriz_movimentada[i])


matriz = [[1, 1, 1, 1],
          [3, 1, 9, 3],
          [3, 1, 0, 1],
          [1, 1, 9, 1]]

# deslizarMatriz(matriz, 'L')









