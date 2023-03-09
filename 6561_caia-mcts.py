#!/usr/bin/env python3
import sys
import random

# Funções utils
def gerarCordenadas(n=5):
    cordenadas = []
    for linha in range(1, n):
        for coluna in range(1, n):
            cordenadas.append(linha * 10 + coluna)
    return cordenadas


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
    def getAcaoPorRodada(self, rodada):
        return RITMO_DO_JOGO[(rodada - 1) % len(RITMO_DO_JOGO)]

    def getCordenadaAleatoria(self):
        return random.choice(CORDENADAS_TABULEIRO)


entrada = sys.stdin.readline()
tabuleiro = Tabuleiro()
game = Game()
if entrada.strip() == "A":
    # jogando como jogador A
    rodada = 1
    while True:
        if entrada.strip() == "Quit":
            break
        if game.getAcaoPorRodada(rodada) != 'deslizar':
            coordenada = game.getCordenadaAleatoria()
            while not tabuleiro.hasPosicaoVazio(coordenada):
                coordenada = game.getCordenadaAleatoria()
            tabuleiro.inserirNoPorCoordenada(coordenada, VALOR_INICIAL_NO, game.getAcaoPorRodada(rodada))
            print(coordenada)
            sys.stdout.flush()
        else:
            comandoDeDeslize = random.choice(list(tabuleiro.MOVIMENTOS_DO_JOGO.keys()))
            print(comandoDeDeslize)
            sys.stdout.flush()
        rodada += 2

        #Prever a jogada do adversário
        entrada = sys.stdin.readline()
        if game.getAcaoPorRodada(rodada-1) != 'deslizar':
            coordenadaDoOponente = int(entrada.strip())
            tabuleiro.inserirNoPorCoordenada(coordenadaDoOponente, VALOR_INICIAL_NO,
                                             game.getAcaoPorRodada(rodada - 1))

else:
    # jogando como jogador B
    rodada = 2
    while True:
        if entrada.strip() == "Quit":
            break
        if game.getAcaoPorRodada(rodada) != 'deslizar':
            coordenada = game.getCordenadaAleatoria()
            while not tabuleiro.hasPosicaoVazio(coordenada):
                coordenada = game.getCordenadaAleatoria()
            tabuleiro.inserirNoPorCoordenada(coordenada, VALOR_INICIAL_NO, game.getAcaoPorRodada(rodada))
            print(coordenada)
            sys.stdout.flush()
        else:
            comandoDeDeslize = random.choice(list(tabuleiro.MOVIMENTOS_DO_JOGO.keys()))
            print(comandoDeDeslize)
            sys.stdout.flush()
        rodada += 2

        # Prever a jogada do adversário
        entrada = sys.stdin.readline()
        if game.getAcaoPorRodada(rodada - 1) != 'deslizar':
            coordenadaDoOponente = int(entrada.strip())
            tabuleiro.inserirNoPorCoordenada(coordenadaDoOponente, VALOR_INICIAL_NO,
                                             game.getAcaoPorRodada(rodada - 1))
