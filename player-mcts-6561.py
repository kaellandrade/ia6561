#!/usr/bin/env python3
import sys
import random
from itertools import chain
from functools import reduce
from colorama import Back, Style
import copy

COR_VERMELHO = 'vermelho'
COR_AZUL = 'azul'
COR_CINZA = 'cinza'

PARA_DIREITA = 'R'
PARA_ESQUERDA = 'L'
PARA_BAIXO = 'D'
PARA_CIMA = 'U'

cores = {
    COR_VERMELHO: Back.RED,
    COR_AZUL: Back.BLUE,
    COR_CINZA: Back.BLACK,
    'branco': Back.WHITE  # Não tem no jogo (controle interno da estrutura)
}
VALOR_INICIAL_NO = 1  # Valor que irá ser dado em cada rodada
VALORES_INICIAIS_NO = [1, 3, 9, 27, None]  # Lista para criar o tabuleiro
RITMO_DO_JOGO = ['azul', 'vermelho', 'cinza', 'deslizar', 'deslizar']


def gerarCoordenadas(n=4):
    """
    Função para gerar uma lista com todas as coodernadas que existem em um tabuleiro/matriz 4x4.
    Exemplo:
        [11, 12, 13, 14, 21, 22, 23, 24, 31, 32, 33, 34, 41, 42, 43, 44]
    :param n:
    :return:
    """
    cordenadas = []
    for linha in range(1, n + 1):
        for coluna in range(1, n + 1):
            cordenadas.append(linha * 10 + coluna)
    return cordenadas


CORDENADAS_TABULEIRO = gerarCoordenadas(4)


class No:
    """
    Classe que representa um No em um tabuleiro. (Vazio ou não)
    """
    valor = None   #TODO: refatorar isso para 0
    cor = 'branco'

    def __init__(self, valor=None, cor='branco'):
        """
        Construtor da classe Nó
        :param valor: Valor do nó
        :param cor: Cor do nó
        """
        self.valor = valor
        self.cor = cor

    def __str__(self):
        """
        Função para formatar a impressão das casas do tabuleiro através da função print()
        :return:
        """
        if self.valor:
            return '{:0>2}'.format(str(self.valor))
        return '  '

    def isNoVazio(self):
        return self.valor is None

    def getValor(self):
        return self.valor

    def getValor2(self):
        if self.isNoVazio():
            return 0
        return self.getValor()

    def getCor(self):
        return self.cor

    def setValor(self, valor):
        self.valor = valor

    def isMesmaConfiguracao(self, no2):
        """
        Verifica se um dado nó possui a mesma configuração que o nó atual.
        """
        return self.getCor() == no2.getCor() and self.getValor() == no2.getValor()


class Tabuleiro:
    """
    Classe que representa o meu tabuleiro.
    """
    matriz = []
    dimensao = 4
    scoreAtualTabuleiro = 0  # pontuação atual do tabuleiro: soma de todos os elementos do tabuleiro

    def __init__(self, dimensao=4, inicializarNos=True):
        """
        Construtor da Classe Tabuleiro.
        Inicia meu tabuleiro com todos os Nós vazios.
        :param dimensao: Dimensão do meu tabuleiro (4 por padrão)
        """
        self.dimensao = dimensao
        if inicializarNos:
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
        self.calcularScoreTabuleiro()


    def limparNoPorCoordenada(self, coordenada):
        """
        Recebe uma coordenada no formato xx e torna seu nó vazio.
        :param coordenada: Inteiro
        :return: Void
        """
        linha, coluna = self._splitCoordenada(coordenada)
        self.matriz[linha][coluna] = No()

    def _splitCoordenada(self, coordenada):
        """
        Recebe uma coordenada xx(padrão do jogo) e retorna uma coordenada válida para a matriz do tabuleiro.
        :param coordenada:
        :return: Void
        """
        linhaParaInserir = (coordenada // 10) - 1  # divide por 10 pra pegar a dezena
        colunaParaInserir = (coordenada % 10) - 1  # obtém o resto da divisão por 10 para pegar a unidade
        return linhaParaInserir, colunaParaInserir

    def hasPosicaoVazio(self, coordenada):
        """
        Recebe uma coordenada no formato xx e verifica se essa posição na matriz/tabuleiro está vazia.
        :param coordenada:
        :return: Booleano
        """
        linhaParaInserir, colunaParaInserir = self._splitCoordenada(coordenada)
        if self.matriz[linhaParaInserir][colunaParaInserir].valor is None:
            return True
        else:
            return False

    def _isolarEspacosVazios(self, lista, movimento):
        """
        Isola os espaços vazios de cada linha da matriz.
        :param lista: Lista de No
        :param movimento: R, L
        :return: Void
        """
        match movimento:
            case 'L':  # De baixo para cima
                j = 0
                for i in range(len(lista)):
                    if lista[i].isNoVazio():
                        j += 1
                    elif lista[i - j].isNoVazio():
                        lista[i - j] = lista[i]
                        lista[i] = No()
            case 'R':  # De cima para baixo
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
        TAMANHO_LISTA = len(lista)
        match movimento:
            case 'L':
                i = 1
                while i < TAMANHO_LISTA:
                    if not lista[i - 1].isNoVazio():
                        noA = lista[i - 1]
                        noB = lista[i]
                        # Mesclando peças (mesma cor e mesmo valor)
                        if noA.getValor() == noB.getValor() and noA.getCor() == noB.getCor():
                            lista[i - 1].setValor(3 * lista[i].getValor())
                            lista[i] = No()
                        # Limpando as casas (Mesmo valor, porém com cores distintas)
                        if noA.getValor() == noB.getValor() and noA.getCor() != noB.getCor():
                            lista[i-1] = No()
                            lista[i] = No()
                    i += 1
            case 'R':
                i = 1
                while i < TAMANHO_LISTA:
                    noA = lista[TAMANHO_LISTA - i]
                    noB = lista[TAMANHO_LISTA - 1 - i]
                    if not noA.isNoVazio():
                        if noA.getValor() == noB.getValor() and noA.getCor() == noB.getCor():
                            noA.setValor(3 * noB.getValor())
                            lista[TAMANHO_LISTA - i - 1] = No()
                        if noA.getValor() == noB.getValor() and noA.getCor() != noB.getCor():
                            lista[TAMANHO_LISTA - i] = No()
                            lista[TAMANHO_LISTA - 1 - i] = No()
                    i += 1

        self._isolarEspacosVazios(lista, movimento)

    def _transporMatriz(self, matriz):
        """
        Função que recebe uma matriz e a modifica para ser equivalente à sua transposta.
        :param matriz:
        :return:
        """
        for i in range(len(matriz)):
            for j in range(i + 1, len(matriz[0])):
                matriz[i][j], matriz[j][i] = matriz[j][i], matriz[i][j]

    def _deslizarBaixo(self):
        """
        Desliza o tabuleiro para baixo utilizando a lógica de transposição de matriz.
        Deslizar uma matriz para baixo é a mesma coisa que deslizar a sua transposta para a direita.
        :return: Void
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
        """
        Desliza o tabuleiro para cima utilizando a lógica de transposição de matriz.
        Deslizar uma matriz m para cima é a mesma coisa que deslizar a sua transposta para a esquerda.
        :return:
        """
        self._transporMatriz(self.matriz)
        for i in range(4):
            self._aplicarRegraLinha(self.matriz[i], PARA_ESQUERDA)
        self._transporMatriz(self.matriz)                              # Retornar para a matriz original

    def isDesLizeValido(self, movimentoDeDeslize):
        """
        Verifica se um movimento de deslize é válido.
        Caso o deslize não mude a configuração do tabuleiro, esse deslize é inválido.
        """
        novoTabuleiro = Tabuleiro(4, False)  # Não quero iniciar os nós, pois irei pegar do tabuleiro original.
        copiaDaMatrizOriginal = self.getCopiaDaMatriz()
        novoTabuleiro.setMatrizNos(copiaDaMatrizOriginal)
        novoTabuleiro.deslizar(movimentoDeDeslize)
        return not self._hasMesmaConfiguracao(novoTabuleiro)

    def _hasMesmaConfiguracao(self, tabuleiro2):
        """
        Verifica se um dado tabuleiro tem a mesma configuração do atual.
        """
        for i in range(len(self.matriz)):
            for j in range(len(self.matriz)):
                if not self.matriz[i][j].isMesmaConfiguracao(tabuleiro2.matriz[i][j]):
                    return False

        return True

    def setMatrizNos(self, matriz):
        self.matriz = matriz

    def getCopiaDaMatriz(self):
        return copy.deepcopy(self.matriz)

    def deslizar(self, lado):
        """
        Desliza o tabuleiro para uma das quatro direções.
        :return: Void
        """
        self.MOVIMENTOS.get(lado)()
        self.calcularScoreTabuleiro()


    def calcularScoreTabuleiro(self):
        """
        Função para calcular a pontuação atual do tabuleiro: somar o atributo valor de todos os nós atuais do tabuleiro.
        :return:
        """
        listaNos = list(chain(*self.matriz))
        self.scoreAtualTabuleiro = reduce(lambda atual, prox: atual + prox.getValor2(), listaNos, 0)


    def getScoreTabuleiro(self):
        """
        Função para retornar a pontuação atual do tabuleiro.
        :return:
        """
        return self.scoreAtualTabuleiro



class Game:
    scoreMaxJogo = 0  # pontuação máxima do jogo, que será dada aos jogadores.
    tabuleiro = None

    def __init__(self, tabuleiro):
        self.tabuleiro = tabuleiro

    def getTabuleiro(self):
        return self.tabuleiro

    def getAcaoPorRodada(self, rodada):
        """
        Função que, através da rodada atual, descobre qual deve ser a minha jogada.
        Ex: estando na rodada x, devo colocar uma peça azul, vermelha, cinza, ou deslizar o tabuleiro?
        :param rodada:
        :return:
        """
        return RITMO_DO_JOGO[(rodada - 1) % len(RITMO_DO_JOGO)]

    def getCordenadaAleatoria(self):
        """
        Função para escolher aleatoriamente uma posição do tabuleiro para o jogador jogar.
        :return:
        """
        return random.choice(CORDENADAS_TABULEIRO)

    def calcularScoreJogo(self):
        """
        Função para atualizar a pontuação máxima durante todo o jogo. Ou seja, a maior pontuação do tabuleiro.
        Essa pontuação representa a pontuação que será dada aos jogadores.
        :return:
        """
        scoreTabuleiro = self.tabuleiro.getScoreTabuleiro()
        if scoreTabuleiro > self.scoreMaxJogo:
            self.scoreMaxJogo = scoreTabuleiro

    def getScoreJogo(self):
        """
        Função para retornar a pontuação máxima do jogo.
        :return:
        """
        return self.scoreMaxJogo


def runCaia():
    """
    Função principal para iniciar um jogador no caia.
    :return:
    """
    entrada = sys.stdin.readline()
    game = Game(Tabuleiro())
    if entrada.strip() == "A":
        # jogando como jogador A
        rodada = 1
        while True:
            # Realizando minha jogada
            if entrada.strip() == "Quit":
                break
            if game.getAcaoPorRodada(rodada) != 'deslizar':
                coordenada = game.getCordenadaAleatoria()
                while not game.getTabuleiro().hasPosicaoVazio(coordenada):
                    coordenada = game.getCordenadaAleatoria()
                game.getTabuleiro().inserirNoPorCoordenada(coordenada, VALOR_INICIAL_NO, game.getAcaoPorRodada(rodada))
                print(coordenada)
                sys.stdout.flush()
            else:
                # Comando de deslize.
                deslizesPossiveis = list(game.getTabuleiro().MOVIMENTOS.keys())
                comandoDeDeslize = random.choice(deslizesPossiveis)

                while not game.getTabuleiro().isDesLizeValido(comandoDeDeslize):
                    comandoDeDeslize = random.choice(list(game.getTabuleiro().MOVIMENTOS.keys()))

                game.getTabuleiro().deslizar(comandoDeDeslize)
                print(comandoDeDeslize)
                sys.stdout.flush()
            rodada += 2

            # Prever a jogada adversária
            entrada = sys.stdin.readline()
            if entrada.strip() == PARA_ESQUERDA:
                game.getTabuleiro().deslizar(PARA_ESQUERDA)

            if entrada.strip() == PARA_DIREITA:
                game.getTabuleiro().deslizar(PARA_DIREITA)

            if entrada.strip() == PARA_CIMA:
                game.getTabuleiro().deslizar(PARA_CIMA)

            if entrada.strip() == PARA_BAIXO:
                game.getTabuleiro().deslizar(PARA_BAIXO)

            if entrada.strip() != "Quit" and game.getAcaoPorRodada(rodada - 1) != 'deslizar':
                coordenadaDoOponente = int(entrada.strip())
                game.getTabuleiro().inserirNoPorCoordenada(coordenadaDoOponente, VALOR_INICIAL_NO,
                                                 game.getAcaoPorRodada(rodada - 1))

    else:
        # jogando como jogador B
        rodada = 2
        while True:
            # Ler a jogada adversária
            entrada = sys.stdin.readline()
            if entrada.strip() == PARA_ESQUERDA:
                game.getTabuleiro().deslizar(PARA_ESQUERDA)

            if entrada.strip() == PARA_DIREITA:
                game.getTabuleiro().deslizar(PARA_DIREITA)

            if entrada.strip() == PARA_CIMA:
                game.getTabuleiro().deslizar(PARA_CIMA)

            if entrada.strip() == PARA_BAIXO:
                game.getTabuleiro().deslizar(PARA_BAIXO)

            if entrada.strip() != "Quit" and game.getAcaoPorRodada(rodada - 1) != 'deslizar':
                coordenadaDoOponente = int(entrada.strip())
                game.getTabuleiro().inserirNoPorCoordenada(coordenadaDoOponente, VALOR_INICIAL_NO,
                                                 game.getAcaoPorRodada(rodada - 1))

            # Realizando minha jogada
            if entrada.strip() == "Quit":
                break
            if game.getAcaoPorRodada(rodada) != 'deslizar':
                coordenada = game.getCordenadaAleatoria()
                while not game.getTabuleiro().hasPosicaoVazio(coordenada):
                    coordenada = game.getCordenadaAleatoria()
                game.getTabuleiro().inserirNoPorCoordenada(coordenada, VALOR_INICIAL_NO, game.getAcaoPorRodada(rodada))
                print(coordenada)
                sys.stdout.flush()
            else:
                comandoDeDeslize = random.choice(list(game.getTabuleiro().MOVIMENTOS.keys()))
                while not game.getTabuleiro().isDesLizeValido(comandoDeDeslize):
                    comandoDeDeslize = random.choice(list(game.getTabuleiro().MOVIMENTOS.keys()))

                game.getTabuleiro().deslizar(comandoDeDeslize)
                print(comandoDeDeslize)
                sys.stdout.flush()
            rodada += 2




def runLocal():
    """
    Função para realizar testes no algoritmo independente do caia
    :return:
    """
    game = Game(Tabuleiro())
    print('Configuração inicial')
    game.getTabuleiro().printTabuleiro()
    game.getTabuleiro().inserirNoPorCoordenada(43, 1, COR_AZUL)
    game.getTabuleiro().inserirNoPorCoordenada(34, 1, COR_VERMELHO)
    game.getTabuleiro().inserirNoPorCoordenada(13, 1, COR_CINZA)

    game.getTabuleiro().inserirNoPorCoordenada(21, 3, COR_VERMELHO)
    game.getTabuleiro().inserirNoPorCoordenada(22, 1, COR_AZUL)
    game.getTabuleiro().inserirNoPorCoordenada(23, 9, COR_AZUL)
    game.getTabuleiro().inserirNoPorCoordenada(24, 3, COR_CINZA)

    game.getTabuleiro().inserirNoPorCoordenada(31, 3, COR_VERMELHO)
    game.getTabuleiro().inserirNoPorCoordenada(32, 1, COR_AZUL)
    game.getTabuleiro().inserirNoPorCoordenada(34, 1, COR_CINZA)

    print('Tabuleiro criado')
    game.getTabuleiro().printTabuleiro()

    print('Pontuacao do game.getTabuleiro(): ', game.getTabuleiro().getScoreTabuleiro())
    game.calcularScoreJogo()

    print('Giro para direita')
    game.getTabuleiro().deslizar(PARA_DIREITA)
    game.getTabuleiro().printTabuleiro()

    game.getTabuleiro().calcularScoreTabuleiro()
    print('Pontuacao do game.getTabuleiro(): ', game.getTabuleiro().getScoreTabuleiro())
    game.calcularScoreJogo()

    print('Giro para cima')
    game.getTabuleiro().deslizar(PARA_CIMA)
    game.getTabuleiro().printTabuleiro()

    game.getTabuleiro().calcularScoreTabuleiro()
    print('Pontuacao do game.getTabuleiro(): ', game.getTabuleiro().getScoreTabuleiro())
    game.calcularScoreJogo()

    print('Depois do giro para esquerda')
    game.getTabuleiro().deslizar(PARA_ESQUERDA)
    game.getTabuleiro().printTabuleiro()

    game.getTabuleiro().calcularScoreTabuleiro()
    print('Pontuacao do game.getTabuleiro(): ', game.getTabuleiro().getScoreTabuleiro())
    game.calcularScoreJogo()

    print('Depois do giro para direita')
    game.getTabuleiro().deslizar(PARA_DIREITA)
    game.getTabuleiro().printTabuleiro()

    game.getTabuleiro().calcularScoreTabuleiro()
    print('Pontuacao do game.getTabuleiro(): ', game.getTabuleiro().getScoreTabuleiro())
    game.calcularScoreJogo()

    print('Depois do giro para baixo')
    game.getTabuleiro().deslizar(PARA_BAIXO)
    game.getTabuleiro().printTabuleiro()

    game.getTabuleiro().calcularScoreTabuleiro()
    print('Pontuacao do game.getTabuleiro(): ', game.getTabuleiro().getScoreTabuleiro())
    game.calcularScoreJogo()

    print('Pontuacao máxima: ', game.getScoreJogo())


if __name__ == "__main__":
    # runCaia()
    runLocal()
