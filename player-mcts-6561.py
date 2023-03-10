#!/usr/bin/env python3
import sys
import random
from colorama import Back, Style


# Funções úteis para modelagem.
def gerarCordenadas(n=4):
    cordenadas = []
    for linha in range(1, n + 1):
        for coluna in range(1, n + 1):
            cordenadas.append(linha * 10 + coluna)
    return cordenadas


COR_VERMELHO = 'vermelho'
COR_AZUL = 'azul'
COR_CINZA = 'cinza'

PARA_DIREITA = 'R'
PARA_ESQUERDA = 'L'
PARA_BAIXO = 'D'
PARA_CIMA = 'U'

cores = {
    COR_VERMELHO: Back.BLUE,
    COR_AZUL: Back.RED,
    COR_CINZA: Back.BLACK,
    'branco': Back.WHITE # Não tem no jogo (controle interno da estrutura)
}
VALOR_INICIAL_NO = 1  # Valor que irá ser dado em cada rodada
VALORES_INICIAIS_NO = [1, 3, 9, 27, None]  # Lista para criar o tabuleiro
RITMO_DO_JOGO = ['azul', 'vermelho', 'cinza', 'deslizar', 'deslizar']

# Lista de inteiros representado as coordenadas do tabuleiro
# |11|12|13|14|
# |21|22|23|24|
# ...
CORDENADAS_TABULEIRO = gerarCordenadas(4)


class No:
    """
    Classe que representa um no no tabuleiro. (Vazio ou não)
    """
    valor = None
    cor = 'branco'
    score = 0

    def __init__(self, valor=None, cor='branco'):
        """
        Construtor da classe Nó
        :param valor: Valor do nó
        :param cor: Cor do nó
        """
        self.valor = valor
        self.cor = cor

    def __str__(self):
        if self.valor:
            return '{:0>2}'.format(str(self.valor))
        return '  '

    def isNoVazio(self):
        return self.valor is None

    def getValor(self):
        return self.valor

    def getCor(self):
        return self.cor

    def setValor(self, valor):
        self.valor = valor


class Tabuleiro:
    """
    Classe que representa o meu tabuleiro.
    """
    matriz = []
    dimensao = 4

    def __init__(self, dimensao=4):
        """
        Construtor da da Classe Tabuleiro
        Inicia meu tabuleiro com todos os Nós vazio.
        :param dimensao: Dimensão do meu tabuleiro (4 por padrão)
        """
        self.dimensao = dimensao
        self._iniciarTabuleiro()
        self.MOVIMENTOS = {
            PARA_BAIXO: self._deslizarBaixo,
            PARA_DIREITA: self._deslizarDireita,
            PARA_ESQUERDA: self._deslizarEsquerda,
            PARA_CIMA: self._deslizarCima
        }

    def printTabuleiro(self):
        """
        Printa o tabuleiro colorido.
        :return:
        """
        for linha in self.matriz:
            for elemento in linha:
                cor = cores[elemento.cor]
                print(cor + str(elemento) + Style.RESET_ALL, end=' ')
            print('\n')

    def _iniciarTabuleiro(self):
        """
        Inicia o tabuleiro com todos os Nós vazios.
        :return: Void
        """
        for i in range(self.dimensao):
            linha = []
            for j in range(self.dimensao):
                novo_no = No()
                linha.append(novo_no)
            self.matriz.append(linha)

    def inserirNoPorCoordenada(self, coordenada, valor, cor):
        """
        Recebe uma coordena no padrão xx e insere no tabuleiro.
        :param coordenada: Inteiro
        :param valor: Inteiro
        :param cor: azul, vermelho, cinza ou branco
        :return: Void
        """
        novoNo = No()
        novoNo.cor = cor
        novoNo.valor = valor
        novoNo.score = 0
        linhaParaInserir, colunaParaInserir = self._splitCoordenada(coordenada)
        self.matriz[linhaParaInserir][colunaParaInserir] = novoNo

    def liparNoPorCordenada(self, coordenada):
        """
        Recebe uma coordenada no formato xx e torna seu nó vazio.
        :param coordenada: Inteiro
        :return: Void
        """
        linha, coluna = self._splitCoordenada(coordenada)
        self.matriz[linha][coluna] = No()

    def _splitCoordenada(self, coordenada):
        """
        Rece uma coordenada xx(padrão do jogo) e retorna uma coordenada válida para a matriz do tabuleiro.
        :param coordenada:
        :return: Void
        """
        linhaParaInserir = (coordenada // 10) - 1  # divide por 10 pra pegar a dezena
        colunaParaInserir = (coordenada % 10) - 1  # obtém o resto da divisão por 10 para pegar a unidade
        return linhaParaInserir, colunaParaInserir

    def hasPosicaoVazio(self, coordenada):
        linhaParaInserir, colunaParaInserir = self._splitCoordenada(coordenada)
        if self.matriz[linhaParaInserir][colunaParaInserir].valor is None:
            return True
        else:
            return False

    def _isolarEspacosVazios(self, lista, movimento):
        """
        Isola os espaços vazios de cada linha da matriz.
        :param lista: lista de No
        :param movimento: R,L
        :return: Void
        """
        match movimento:
            case 'L':  ## De baixo para cima
                j = 0
                for i in range(len(lista)):
                    if lista[i].isNoVazio():
                        j += 1
                    elif lista[i - j].isNoVazio():
                        lista[i - j] = lista[i]
                        lista[i] = No()
            case 'R':  ## De cima para baixo
                j = 0
                for i in range(len(lista), 0, -1):
                    if lista[i - 1].isNoVazio():
                        j += 1
                    elif lista[i + j - 1].isNoVazio():
                        lista[i + j - 1] = lista[i - 1]
                        lista[i - 1] = No()

    def _aplicarRegraLinha(self, lista, movimento):
        """
        Aplica a regra do jogo em uma linha do tabuleiro.
        :param lista: No
        :param movimento: R, L
        :return: Void
        """
        self._isolarEspacosVazios(lista, movimento)
        match movimento:
            case 'L':
                i = 1
                while i < len(lista):
                    if not lista[i - 1].isNoVazio():
                        if lista[i - 1].getValor() == lista[i].getValor():
                            lista[i - 1].setValor(3 * lista[i].getValor())
                            lista[i] = No()
                    i += 1
            case 'R':
                i = 1
                while i < len(lista):
                    if not lista[len(lista) - i].isNoVazio():
                        if lista[len(lista) - 1 - i].getValor() == lista[len(lista) - i].getValor():
                            lista[len(lista) - i].setValor(3 * lista[len(lista) - i - 1].getValor())
                            lista[len(lista) - i - 1] = No()
                    i += 1

        self._isolarEspacosVazios(lista, movimento)

    def _transporMatriz(self, matriz):
        for i in range(len(matriz)):
            for j in range(i + 1, len(matriz[0])):
                matriz[i][j], matriz[j][i] = matriz[j][i], matriz[i][j]

    def _deslizarBaixo(self):
        # TODO: utilizar a lógica de transposição
        """
        Desliza o tabuleiro para baixo utilizando a lógica de transposição de matriz.
        Deslizar uma matriz m para baixo é a mesma coisa que deslizar a sua transposta para a direita.
        :return:
        """
        self._transporMatriz(self.matriz)
        for i in range(4):
            self._aplicarRegraLinha(self.matriz[i], PARA_DIREITA)
        self._transporMatriz(self.matriz)  # Retornar para a matriz original

    def _deslizarDireita(self):
        """
        Desliza os tabuleiro para direita.
        :return: Void
        """
        for i in range(self.dimensao):
            self._aplicarRegraLinha(self.matriz[i], PARA_DIREITA)

    def _deslizarEsquerda(self):
        """
        Desliza o tabuleiro para esquerda.
        :return:
        """
        for i in range(self.dimensao):
            self._aplicarRegraLinha(self.matriz[i], PARA_ESQUERDA)


    def _deslizarCima(self):
        # TODO: utilizar a lógica de transposição
        """
        Desliza o tabuleiro para cima utilizando a lógica de transposição de matriz.
        Deslizar uma matriz m para cima é a mesma coisa que deslizar a sua transposta para a esquerda.
        :return:
        """
        self._transporMatriz(self.matriz)
        for i in range(4):
            self._aplicarRegraLinha(self.matriz[i], PARA_ESQUERDA)
        self._transporMatriz(self.matriz)                              # Retornar para a matriz original


    def deslizar(self, lado):
        self.MOVIMENTOS.get(lado)()


class Game:
    def getAcaoPorRodada(self, rodada):
        return RITMO_DO_JOGO[(rodada - 1) % len(RITMO_DO_JOGO)]

    def getCordenadaAleatoria(self):
        return random.choice(CORDENADAS_TABULEIRO)


def runCaia():
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
                comandoDeDeslize = random.choice(list(tabuleiro.MOVIMENTOS.keys()))
                print(comandoDeDeslize)
                sys.stdout.flush()
            rodada += 2

            # Prever a jogada do adversário
            entrada = sys.stdin.readline()
            if game.getAcaoPorRodada(rodada - 1) != 'deslizar':
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
                comandoDeDeslize = random.choice(list(tabuleiro.MOVIMENTOS.keys()))
                print(comandoDeDeslize)
                sys.stdout.flush()
            rodada += 2

            # Prever a jogada do adversário
            entrada = sys.stdin.readline()
            if game.getAcaoPorRodada(rodada - 1) != 'deslizar':
                coordenadaDoOponente = int(entrada.strip())
                tabuleiro.inserirNoPorCoordenada(coordenadaDoOponente, VALOR_INICIAL_NO,
                                                 game.getAcaoPorRodada(rodada - 1))


if __name__ == "__main__":
    # runCaia()
    tabuleiro = Tabuleiro()
    tabuleiro.inserirNoPorCoordenada(11, 1, COR_VERMELHO)
    tabuleiro.inserirNoPorCoordenada(12, 1, COR_AZUL)
    tabuleiro.inserirNoPorCoordenada(14, 1, COR_CINZA)

    tabuleiro.inserirNoPorCoordenada(31, 1, COR_VERMELHO)
    tabuleiro.inserirNoPorCoordenada(32, 1, COR_AZUL)
    tabuleiro.inserirNoPorCoordenada(24, 1, COR_CINZA)
    tabuleiro.printTabuleiro()

    print('Depois do giro para esquerda')
    tabuleiro.deslizar(PARA_ESQUERDA)
    tabuleiro.printTabuleiro()
    print('Depois do giro para direita')
    tabuleiro.deslizar(PARA_DIREITA)
    tabuleiro.printTabuleiro()
    print('Depois do giro para cima')
    tabuleiro.deslizar(PARA_CIMA)
    tabuleiro.printTabuleiro()
    print('Depois do giro para baixo')
    tabuleiro.deslizar(PARA_BAIXO)
    tabuleiro.printTabuleiro()

