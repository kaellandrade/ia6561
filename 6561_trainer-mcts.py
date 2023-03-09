#!/usr/bin/env python3

import sys
import random
from colorama import Back, Style


# Funções utils
def gerarCordenadas(n=5):
    cordenadas = []
    for linha in range(1, n):
        for coluna in range(1, n):
            cordenadas.append(linha * 10 + coluna)
    return cordenadas


cores = {
    'azul': Back.BLUE,
    'vermelho': Back.RED,
    'cinza': Back.BLACK,
    'branco': Back.WHITE
}
VALOR_INICIAL_NO = 1  # Valor que irá ser dado em cada rodada
VALORES_INICIAIS_NO = [1, 3, 9, 27, None]  # Lista para criar o tabuleiro
RITMO_DO_JOGO = ['azul', 'vermelho', 'cinza', 'deslizar', 'deslizar']
CORDENADAS_TABULEIRO = gerarCordenadas(5)


class No:
    valor = None
    cor = 'branco'
    score = 0

    def __init__(self, valor=None, cor='branco'):
        self.valor = valor
        self.cor = cor

    def __str__(self):
        if self.valor:
            return '{:0>2}'.format(str(self.valor))
        return '  '


class Tabuleiro:
    matriz = []
    dimensao = 4

    def __init__(self, dimensao=4):
        self.dimensao = dimensao
        self._iniciarTabuleiro(dimensao)
        self.MOVIMENTOS_DO_JOGO = {
            'D': self.deslizarBaixo,
            'R': self.deslizarDireita,
            'L': self.deslizarEsquerda,
            'U': self.deslizarCima
        }

    def _iniciarTabuleiro(self, n):
        for i in range(n):
            linha = []
            for j in range(n):
                novo_no = No()
                linha.append(novo_no)
            self.matriz.append(linha)

    def printTabuleiro(self, ):
        for linha in self.matriz:
            for elemento in linha:
                cor = cores[elemento.cor]
                print(cor + str(elemento) + Style.RESET_ALL, end=' ')
            print('\n')

    def inserirNoPorCoordenada(self, coordenada, valor, cor):
        novoNo = No()
        novoNo.cor = cor
        novoNo.valor = valor
        novoNo.score = 0
        linhaParaInserir, colunaParaInserir = self.splitCoordenada(coordenada)
        self.matriz[linhaParaInserir][colunaParaInserir] = novoNo

    def liparNoPorCordenada(self, coordenada):
        linha, coluna = self.splitCoordenada(coordenada)
        self.matriz[linha][coluna] = No()

    def splitCoordenada(self, coordenada):
        linhaParaInserir = (coordenada // 10) - 1  # divide por 10 pra pegar a dezena
        colunaParaInserir = (coordenada % 10) - 1  # obtém o resto da divisão por 10 para pegar a unidade
        return linhaParaInserir, colunaParaInserir

    def hasPosicaoVazio(self, coordenada):
        linhaParaInserir, colunaParaInserir = self.splitCoordenada(coordenada)
        if self.matriz[linhaParaInserir][colunaParaInserir].valor is None:
            return True
        else:
            return False

    def deslizarBaixo(self):
        print('deslizar para baixo')

    def deslizarDireita(self):
        print('deslizar para direita')

    def deslizarEsquerda(self):
        print('deslizar para esquerda')

    def deslizarCima(self):
        print('deslizar para cima')

    def deslizar(self, lado):
        self.MOVIMENTOS_DO_JOGO.get(lado)()


class Game:
    # tabuleiro = Tabuleiro()
    # TODO: Continuar logica aleatória do servidor.
    def __init__(self):
        entrada = sys.stdin.readline()
        if entrada.strip() == "A":
            rodada = 1
            while True:
                entrada = sys.stdin.readline()
                if (entrada.strip() == "Quit"):
                    break
                if self._getAcaoPorRodada(rodada) != 'deslizar':
                    coordenada = self._getCordenadaAleatoria()
                    while not tabuleiro.hasPosicaoVazio(coordenada):
                        coordenada = self._getCordenadaAleatoria()
                    tabuleiro.inserirNoPorCoordenada(coordenada, VALOR_INICIAL_NO, self._getAcaoPorRodada(rodada))
                    print(coordenada)
                    sys.stdout.flush()
                else:
                    comandoDeDeslize = random.choice(list(tabuleiro.MOVIMENTOS_DO_JOGO.keys()))
                    print(comandoDeDeslize)
                    sys.stdout.flush()
                rodada += 2
                entrada = sys.stdin.readline()
                coordenadaDoOponente = int(entrada.strip())
                tabuleiro.inserirNoPorCoordenada(coordenadaDoOponente, VALOR_INICIAL_NO,
                                                 self._getAcaoPorRodada(rodada - 1))
        else:
            # jogando como jogador B
            rodada = 2
            while True:
                entrada = sys.stdin.readline()
                if (entrada.strip() == "Quit"):
                    break

                if self._getAcaoPorRodada(rodada) != 'deslizar':
                    coordenada = self._getCordenadaAleatoria()
                    while not tabuleiro.hasPosicaoVazio(coordenada):
                        coordenada = self._getCordenadaAleatoria()
                    tabuleiro.inserirNoPorCoordenada(coordenada, VALOR_INICIAL_NO, self._getAcaoPorRodada(rodada))
                    print(coordenada)
                    sys.stdout.flush()
                else:
                    comandoDeDeslize = random.choice(list(tabuleiro.MOVIMENTOS_DO_JOGO.keys()))
                    print(comandoDeDeslize)
                    sys.stdout.flush()
                rodada += 2
                entrada = sys.stdin.readline()
                coordenadaDoOponente = int(entrada.strip())
                tabuleiro.inserirNoPorCoordenada(coordenadaDoOponente, VALOR_INICIAL_NO,
                                                 self._getAcaoPorRodada(rodada - 1))

    def _getAcaoPorRodada(self, rodada):
        return RITMO_DO_JOGO[(rodada - 1) % len(RITMO_DO_JOGO)]

    def _getCordenadaAleatoria(self):
        return random.choice(CORDENADAS_TABULEIRO)


tabuleiro = Tabuleiro()

tabuleiro.printTabuleiro()
tabuleiro.inserirNoPorCoordenada(11, 1, 'azul')
tabuleiro.inserirNoPorCoordenada(43, 1, 'vermelho')
print('Após inserir o nó\n')
tabuleiro.printTabuleiro()
print(tabuleiro.hasPosicaoVazio(43))

tabuleiro.deslizar('U')
tabuleiro.deslizar('D')
tabuleiro.deslizar('R')
tabuleiro.deslizar('L')

tabuleiro.liparNoPorCordenada(43)

tabuleiro.printTabuleiro()