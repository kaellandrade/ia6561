#!/usr/bin/env python3
import math
import sys
import copy
import random
import numpy as np
from itertools import chain
from functools import reduce
from colorama import Back, Style
from math import sqrt
from collections import defaultdict

COR_VERMELHO = 'vermelho'
COR_AZUL = 'azul'
COR_CINZA = 'cinza'
COR_BRANCO = 'branco'

PARA_DIREITA = 'R'
PARA_ESQUERDA = 'L'
PARA_BAIXO = 'D'
PARA_CIMA = 'U'

cores = {
    COR_VERMELHO: Back.RED,
    COR_AZUL: Back.BLUE,
    COR_CINZA: Back.BLACK,
    COR_BRANCO: Back.WHITE  # Branco não tem no jogo (controle interno da estrutura)
}
VALOR_INICIAL_POR_RODADA = 1
RITMO_DO_JOGO = ['azul', 'vermelho', 'cinza', 'deslizar', 'deslizar']
MOVIMENTOS_DESLIZES = [PARA_DIREITA, PARA_ESQUERDA, PARA_BAIXO, PARA_CIMA]

C = sqrt(2)  # Constante do Exploration
MAX_DEPTH = 8  # Profundidade máxima que as simulações Monte Carlo irão alcançar
QTD_SIMULACOES = 12  # Quantidade de simulações Monte Carlo que serão feitas

class No:
    """
    Classe que representa um No em um tabuleiro. (Vazio ou não)
    """
    valor = 0
    cor = COR_BRANCO

    def __init__(self, valor=0, cor=COR_BRANCO):
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
        """
        Verifica se um dado nó está vazio (com valor 0).
        """
        return self.valor == 0

    def getValor(self):
        """
        Retorna o valor do Nó
        """
        return self.valor

    def getCor(self):
        """
        Retorna a cor do Nó.
        """
        return self.cor

    def setValor(self, valor):
        """
        Seta o valor do Nó.
        """
        self.valor = valor

    def isMesmaConfiguracao(self, no2):
        """
        Verifica se um dado Nó possui a mesma configuração que o nó atual.
        """
        return self.getCor() == no2.getCor() and self.getValor() == no2.getValor()


class Tabuleiro:
    """
    Classe que representa um tabuleiro
    """
    matriz = []
    dimensao = 4
    scoreAtualTabuleiro = 0  # pontuação atual do tabuleiro: soma de todos os elementos do tabuleiro

    def __init__(self, dimensao=4, inicializarNos=True):
        """
        Construtor da Classe Tabuleiro.
        Inicia meu tabuleiro com todos os Nós vazios (Por padrão).
        :param dimensao: Dimensão do meu tabuleiro (4 por padrão)
        :param inicializarNos: Inicializar os nós do tabuleiro.
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

    def getDimensao(self):
        return self.dimensao

    def setScore(self, scoreAtualTabuleiro):
        self.scoreAtualTabuleiro = scoreAtualTabuleiro

    def _iniciarTabuleiro(self):
        """
        Inicia o tabuleiro com todos os Nós vazios.
        Caso essa função não seja executada a matriz estará vazia []
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
        linhaParaInserir, colunaParaInserir = self._splitCoordenada(coordenada) # Destructuring
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
        Recebe uma coordenada xx(padrão do caia) e retorna uma coordenada válida para a matriz do tabuleiro.
        :param coordenada:
        :return: Void
        """
        linhaParaInserir = (coordenada // 10) - 1  # divide por 10 pra pegar a dezena
        colunaParaInserir = (coordenada % 10) - 1  # obtém o resto da divisão por 10 para pegar a unidade
        return linhaParaInserir, colunaParaInserir

    def getCoordenadasVazias(self):
        coordenadasVazias = []
        for i in range(self.dimensao):
            for j in range(self.dimensao):
                if self.matriz[i][j].isNoVazio():
                    coordenada = int(str(i+1) + str(j+1)) # Todo usar _splitCoordenada depois
                    coordenadasVazias.append(coordenada)
        return coordenadasVazias

    def hasPosicaoVazio(self, coordenada):
        """
        Recebe uma coordenada no formato xx e verifica se essa posição na matriz/tabuleiro está vazia.
        :param coordenada:
        :return: Booleano
        """
        linhaParaInserir, colunaParaInserir = self._splitCoordenada(coordenada) #Destructuring
        if not bool(self.matriz[linhaParaInserir][colunaParaInserir].valor):
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
        if PARA_ESQUERDA == movimento:  # De baixo para cima
            j = 0
            for i in range(len(lista)):
                if lista[i].isNoVazio():
                    j += 1
                elif lista[i - j].isNoVazio():
                    lista[i - j] = lista[i]
                    lista[i] = No()

        if PARA_DIREITA == movimento:  # De cima para baixo
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
        if movimento == PARA_ESQUERDA:
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
        if movimento == PARA_DIREITA:
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

    def isDeslizeValido(self, movimentoDeDeslize):
        """
        Verifica se um movimento de deslize é válido.
        Caso o deslize não mude a configuração do tabuleiro, esse deslize é inválido.
        """
        novoTabuleiro = Tabuleiro(4, False)  # Não quero iniciar os nós, pois irei pegar do tabuleiro original. (matriz= [])
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
        :lado: PARA_DIREITA, PARA_ESQUERDA, PARA_BAIXO e PARA_CIMA
        """
        self.MOVIMENTOS.get(lado)()

        self.calcularScoreTabuleiro()

    def calcularScoreTabuleiro(self):
        """
        Função para calcular a pontuação atual do tabuleiro: somar o atributo valor de todos os nós do tabuleiro.
        :return: Void
        """
        listaNos = list(chain(*self.matriz))
        self.scoreAtualTabuleiro = reduce(lambda atual, prox: atual + prox.getValor(), listaNos, 0)

    def getScoreTabuleiro(self):
        """
        Função para retornar a pontuação atual do tabuleiro.
        :return:
        """
        return self.scoreAtualTabuleiro

    def gerarCoordenadas(self):
        """
        Função para gerar uma lista com todas as coodernadas que existem no tabuleiro
        Exemplo:
            [11, 12, 13, 14, 21, 22, ...]
        :return:
        """
        cordenadas = []
        for linha in range(1, self.dimensao + 1):
            for coluna in range(1, self.dimensao + 1):
                cordenadas.append(linha * 10 + coluna)
        return cordenadas


class Game:
    """
    Classe que representa um game, com uma determinada configuração de tabuleiro, scoreMax do jogo e uma rodada.
    """
    scoreMaxJogo = 0  # pontuação máxima do jogo, que será dada aos jogadores.
    tabuleiro = None
    rodada = None

    def __init__(self, tabuleiro, rodada=1):
        self.tabuleiro = tabuleiro
        self.rodada = rodada

    def setRodada(self, rodada):
        self.rodada = rodada

    def getRodada(self):
        return self.rodada

    def getTabuleiro(self):
        """
        Retorna o tabuleiro do jogo.
        :return: Tabuleiro()
        """
        return self.tabuleiro

    def getAcaoPorRodada(self, rodada=0):
        """
        Função que, através da rodada atual, descobre qual deve ser a minha jogada.
        Ex: estando na rodada x, devo colocar uma peça azul, vermelha, cinza, ou deslizar o tabuleiro?
        :param rodada:
        :return: String -> 'azul', 'vermelho', 'cinza', 'deslizar' ou 'deslizar'
        """
        if rodada:
            return RITMO_DO_JOGO[(rodada - 1) % len(RITMO_DO_JOGO)]

        return RITMO_DO_JOGO[(self.rodada - 1) % len(RITMO_DO_JOGO)]

    def getCordenadaAleatoria(self):
        """
        Função para escolher aleatoriamente uma posição do tabuleiro para o jogador jogar.
        :return: Int -> 11, 12, 13, 14, 21, 22, 23, 24, 31, 32, 33, 34, 41, 42, 43 ou 44
        """
        coordenadasDoTabuleiro = self.tabuleiro.gerarCoordenadas()
        return random.choice(coordenadasDoTabuleiro)

    def calcularScoreJogo(self):
        """
        Função para atualizar a pontuação máxima durante todo o jogo.
        Ou seja, a maior pontuação do tabuleiro.
        Essa pontuação representa a pontuação que será dada aos jogadores.
        :return: Int
        """
        scoreTabuleiro = self.tabuleiro.getScoreTabuleiro()
        if scoreTabuleiro > self.scoreMaxJogo:
            self.scoreMaxJogo = scoreTabuleiro

    def getScoreJogo(self):
        """
        Função para retornar a pontuação máxima do jogo.
        """
        return self.scoreMaxJogo

    def setTabuleiro(self, tabuleiro):
        self.tabuleiro = tabuleiro

    def verificarFimDeJogo(self):
        """
        Verifica o fim do jogo.
        """
        acaoAtualNaRodada = self.getAcaoPorRodada()
        acaoAnterior = self.getAcaoPorRodada(self.getRodada()-1)

        # criar cópia do tabuleiro para simular um deslize
        dimensao = self.getTabuleiro().dimensao
        tabuleiroCopia = Tabuleiro(dimensao, False)
        copiaMatriz = self.getTabuleiro().getCopiaDaMatriz()
        tabuleiroCopia.setMatrizNos(copiaMatriz)

        qtdCoordenadasVazias = len(tabuleiroCopia.getCoordenadasVazias())

        # Se não houver casas vazias quando o jogador deve colocar uma peça, o jogo termina.
        if qtdCoordenadasVazias == 0 and acaoAtualNaRodada != 'deslizar':
            return True

        # O jogo termina quando o tabuleiro estiver vazio após o primeiro slide
        if qtdCoordenadasVazias == 16 and acaoAtualNaRodada == 'deslizar' and acaoAnterior == 'deslizar':
            return True

        # Se não houver movimento de slide válido quando um movimento de slide for necessário, o jogo termina
        if acaoAtualNaRodada == 'deslizar':
            for movimento in MOVIMENTOS_DESLIZES:
                # Se houver pelo menos um deslize válido, já retorne que não é fim de jogo
                if tabuleiroCopia.isDeslizeValido(movimento):
                    return False
            return True

        return False

    def get_legal_actions(self, rodada):
        """
        Função para retornar uma lista de todas as ações possíveis de realizar dado um estado do tabuleiro.
        """
        acao = self.getAcaoPorRodada(rodada)
        if acao != 'deslizar':
            return self.getTabuleiro().getCoordenadasVazias()
        else:
            movimentosPossiveis = []
            for movimento in MOVIMENTOS_DESLIZES:
                if self.getTabuleiro().isDeslizeValido(movimento):
                    movimentosPossiveis.append(movimento)
            return movimentosPossiveis

    def is_game_over(self):
        """
        Verificar fim de jogo.
        """
        return self.verificarFimDeJogo()

    def game_result(self):
        """
        Função que retorna o maior score de jogo obtido por uma simulação do rollout.
        """
        return self.getScoreJogo()

    def move(self, action):
        """
        Função para realizar um movimento de jogo, seja adicionar uma peça ou deslizar o tabuleiro. A função retorna
        o novo estado gerado a partir dessa ação.
        """
        tabuleiroAtual = self.getTabuleiro()

        scoreTabuleiro = tabuleiroAtual.getScoreTabuleiro()
        matriz = tabuleiroAtual.getCopiaDaMatriz()
        dimensao = tabuleiroAtual.getDimensao()
        novoTabuleiro = Tabuleiro(dimensao, False)

        novoTabuleiro.setScore(scoreTabuleiro)
        novoTabuleiro.setMatrizNos(matriz)

        newState = Game(novoTabuleiro, self.getRodada())

        if action not in MOVIMENTOS_DESLIZES:
            newState.getTabuleiro().inserirNoPorCoordenada(action, VALOR_INICIAL_POR_RODADA, self.getAcaoPorRodada())
        else:
            newState.getTabuleiro().deslizar(action)

        return newState


class MonteCarloTreeSearchNode:
    """
    Representa a arvore Monte Carlo
    """
    def __init__(self, state, parent=None, parent_action=None):
        """
        Inicia os atributos da arvore.
        """
        self.state = state  # Estado do tabuleiro (Tabuleiro)
        self.parent = parent  # No pai
        self.parent_action = parent_action  # A ação que gerou o No atual, exceto a raiz.
        self.children = []  # Contém os filhos do no atual.
        self._number_of_visits = 0  # Numero de veses que o nó atual foi visitado.
        self._results = defaultdict(int)  # Dicionario contador
        self._results[1] = 0  # Vitorias
        self._untried_actions = None  # Representa a lista de todas as ações possíveis
        self._untried_actions = self.untried_actions()  # Ações não tentadas


    def untried_actions(self):
        """
        Retorna a lista de ações não experimentadas de um determinado estado.
        """
        self._untried_actions = self.state.get_legal_actions(self.state.getRodada())
        return self._untried_actions

    def q(self):
        """
        Retorna a diferença de vitórias e derrotas.
        TODO: Derrotas ??
        """
        wins = self._results[1]
        return wins

    def n(self):
        """
        Retorna o número de vezes que cada nó é visitado.
        """
        return self._number_of_visits

    def expand(self):
        """
        Realiza a expansão do No.
        """
        action = self._untried_actions.pop()
        next_state = self.state.move(action)
        child_node = MonteCarloTreeSearchNode(
            next_state, parent=self, parent_action=action)

        self.children.append(child_node)
        return child_node

    def is_terminal_node(self):
        """
        Veririfica se é um nó terminal, ou seja, fim de jogo.
        """
        return self.state.is_game_over()

    def rollout(self):
        """
        Função para a etapa de simulação Monte Carlo
        """
        current_rollout_state = self.state
        depth = 0
        while not current_rollout_state.is_game_over() and depth <= MAX_DEPTH:
            current_rollout_state.setRodada(self.state.getRodada() + 1)
            possible_moves = current_rollout_state.get_legal_actions(current_rollout_state.getRodada())
            # if len(possible_moves) == 0:
            #     break
            action = self.rollout_policy(possible_moves)
            current_rollout_state = current_rollout_state.move(action)
            depth += 1
            current_rollout_state.calcularScoreJogo()
        return current_rollout_state.game_result()

    def backpropagate(self, reward):
        """
        Função para a etapa de backpropagation Monte Carlo. Atualiza as estatísticas do No.
        """
        self._number_of_visits += 1.  # Incrementa visitas
        self._results[1] += reward  # Incrementa a vitória ou a derrota.
        if self.parent:
            self.parent.backpropagate(reward)

    def is_fully_expanded(self):
        """
        Verifica se o Nó foi totalmente expandido.
        """
        return len(self._untried_actions) == 0

    def best_child(self, c_param=C):
        """
        Função que seleciona o melhor filho no array de filhos.
        O primeiro termo da fórmula é exploitation e o segundo é o exploration.
        """
        choices_weights = [(c.q() / c.n()) + 2 * c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in
                           self.children]
        return self.children[np.argmax(choices_weights)]

    def rollout_policy(self, possible_moves):
        """
        Função que define a política aleatória para a etapa de simulação. Seleciona aleatoriamente um movimento.
        """
        return possible_moves[np.random.randint(len(possible_moves))]

    def _tree_policy(self):
        """
        Função que seleciona o no para executar o rollout, seguindo a política definida (UCT).
        """
        current_node = self
        while not current_node.is_terminal_node():
            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node

    def best_action(self):
        """
        Função para iniciar a execução do algoritmo MCTS TODO: Refatorar para best_action UCTSearch
        """
        simulation_no = QTD_SIMULACOES
        for i in range(simulation_no):
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)
        return self.best_child()


def runCaia():
    """
    Função principal para iniciar um jogador no caia.
    :return:
    """
    entrada = sys.stdin.readline()
    gameCaia = Game(Tabuleiro())
    if entrada.strip() == "A":
        # jogando como jogador A
        gameCaia.setRodada(1)
        while True:
            # Realizando minha jogada
            if entrada.strip() == "Quit":
                break

            tabuleiro = Tabuleiro(gameCaia.getTabuleiro().getDimensao(), False)
            copiaMatriz = gameCaia.getTabuleiro().getCopiaDaMatriz()
            tabuleiro.setMatrizNos(copiaMatriz)
            gameCopia = Game(tabuleiro)
            gameCopia.setRodada(gameCaia.getRodada())
            root = MonteCarloTreeSearchNode(gameCopia)
            selected_node = root.best_action()

            if selected_node.parent_action not in MOVIMENTOS_DESLIZES:
                gameCaia.getTabuleiro().inserirNoPorCoordenada(selected_node.parent_action, VALOR_INICIAL_POR_RODADA,
                                                               gameCaia.getAcaoPorRodada())
                print(selected_node.parent_action)
                sys.stdout.flush()
            else:
                gameCaia.getTabuleiro().deslizar(selected_node.parent_action)
                print(selected_node.parent_action)
                sys.stdout.flush()

            gameCaia.setRodada(gameCaia.getRodada() + 2)

            # Prever a jogada adversária
            entrada = sys.stdin.readline()
            if entrada.strip() == PARA_ESQUERDA:
                gameCaia.getTabuleiro().deslizar(PARA_ESQUERDA)

            if entrada.strip() == PARA_DIREITA:
                gameCaia.getTabuleiro().deslizar(PARA_DIREITA)

            if entrada.strip() == PARA_CIMA:
                gameCaia.getTabuleiro().deslizar(PARA_CIMA)

            if entrada.strip() == PARA_BAIXO:
                gameCaia.getTabuleiro().deslizar(PARA_BAIXO)

            rodada = gameCaia.getRodada()
            if entrada.strip() != "Quit" and gameCaia.getAcaoPorRodada(rodada - 1) != 'deslizar':
                coordenadaDoOponente = int(entrada.strip())
                gameCaia.getTabuleiro().inserirNoPorCoordenada(coordenadaDoOponente, VALOR_INICIAL_POR_RODADA,
                                                           gameCaia.getAcaoPorRodada(rodada - 1))

    else:
        # jogando como jogador B
        gameCaia.setRodada(2)
        while True:
            # Ler a jogada adversária
            entrada = sys.stdin.readline()
            if entrada.strip() == PARA_ESQUERDA:
                gameCaia.getTabuleiro().deslizar(PARA_ESQUERDA)

            if entrada.strip() == PARA_DIREITA:
                gameCaia.getTabuleiro().deslizar(PARA_DIREITA)

            if entrada.strip() == PARA_CIMA:
                gameCaia.getTabuleiro().deslizar(PARA_CIMA)

            if entrada.strip() == PARA_BAIXO:
                gameCaia.getTabuleiro().deslizar(PARA_BAIXO)

            rodada = gameCaia.getRodada()
            if entrada.strip() != "Quit" and gameCaia.getAcaoPorRodada(rodada - 1) != 'deslizar':
                coordenadaDoOponente = int(entrada.strip())
                gameCaia.getTabuleiro().inserirNoPorCoordenada(coordenadaDoOponente, VALOR_INICIAL_POR_RODADA,
                                                               gameCaia.getAcaoPorRodada(rodada - 1))

            # Realizando minha jogada
            if entrada.strip() == "Quit":
                break

            tabuleiro = Tabuleiro(gameCaia.getTabuleiro().getDimensao(), False)
            copiaMatriz = gameCaia.getTabuleiro().getCopiaDaMatriz()
            tabuleiro.setMatrizNos(copiaMatriz)
            gameCopia = Game(tabuleiro)
            gameCopia.setRodada(gameCaia.getRodada())
            root = MonteCarloTreeSearchNode(gameCopia)
            selected_node = root.best_action()

            if selected_node.parent_action not in MOVIMENTOS_DESLIZES:
                gameCaia.getTabuleiro().inserirNoPorCoordenada(selected_node.parent_action, VALOR_INICIAL_POR_RODADA,
                                                               gameCaia.getAcaoPorRodada())
                print(selected_node.parent_action)
                sys.stdout.flush()
            else:
                gameCaia.getTabuleiro().deslizar(selected_node.parent_action)
                print(selected_node.parent_action)
                sys.stdout.flush()

            gameCaia.setRodada(gameCaia.getRodada() + 2)


def runLocal():
    """
    Função para realizar testes no algoritmo independente do caia
    :return:
    """
    # game = Game(Tabuleiro())
    #
    # game.getTabuleiro().inserirNoPorCoordenada(11, 81, COR_AZUL)
    # game.getTabuleiro().inserirNoPorCoordenada(21, 27, COR_AZUL)
    # game.getTabuleiro().inserirNoPorCoordenada(31, 9, COR_AZUL)
    # game.getTabuleiro().inserirNoPorCoordenada(41, 3, COR_AZUL)
    #
    # print('Configuração inicial')
    # game.getTabuleiro().printTabuleiro()
    #
    # game.setRodada(6)
    # root = MonteCarloTreeSearchNode(game)
    # selected_node = root.best_action()
    # print(selected_node.parent_action)
    # game.getTabuleiro().inserirNoPorCoordenada(selected_node.parent_action, 1, game.getAcaoPorRodada())
    # game.getTabuleiro().printTabuleiro()
    #
    # game.setRodada(7)
    # root = MonteCarloTreeSearchNode(game)
    # selected_node = root.best_action()
    # print(selected_node.parent_action)
    # game.getTabuleiro().inserirNoPorCoordenada(selected_node.parent_action, 1, game.getAcaoPorRodada())
    # game.getTabuleiro().printTabuleiro()
    #
    # game.setRodada(8)
    # root = MonteCarloTreeSearchNode(game)
    # selected_node = root.best_action()
    # print(selected_node.parent_action)
    # game.getTabuleiro().inserirNoPorCoordenada(selected_node.parent_action, 1, game.getAcaoPorRodada())
    # game.getTabuleiro().printTabuleiro()
    #
    # game.setRodada(9)
    # root = MonteCarloTreeSearchNode(game)
    # selected_node = root.best_action()
    # print(selected_node.parent_action)
    # game.getTabuleiro().deslizar(selected_node.parent_action)
    # game.getTabuleiro().printTabuleiro()
    #
    # game.setRodada(10)
    # root = MonteCarloTreeSearchNode(game)
    # selected_node = root.best_action()
    # print(selected_node.parent_action)
    # game.getTabuleiro().deslizar(selected_node.parent_action)
    # game.getTabuleiro().printTabuleiro()
    #
    # game.setRodada(11)
    # root = MonteCarloTreeSearchNode(game)
    # selected_node = root.best_action()
    # print(selected_node.parent_action)
    # game.getTabuleiro().inserirNoPorCoordenada(selected_node.parent_action, 1, game.getAcaoPorRodada())
    # game.getTabuleiro().printTabuleiro()
    #
    # game.setRodada(12)
    # root = MonteCarloTreeSearchNode(game)
    # selected_node = root.best_action()
    # print(selected_node.parent_action)
    # game.getTabuleiro().inserirNoPorCoordenada(selected_node.parent_action, 1, game.getAcaoPorRodada())
    # game.getTabuleiro().printTabuleiro()
    #
    # game.setRodada(13)
    # root = MonteCarloTreeSearchNode(game)
    # selected_node = root.best_action()
    # print(selected_node.parent_action)
    # game.getTabuleiro().inserirNoPorCoordenada(selected_node.parent_action, 1, game.getAcaoPorRodada())
    # game.getTabuleiro().printTabuleiro()
    #
    # game.setRodada(14)
    # root = MonteCarloTreeSearchNode(game)
    # selected_node = root.best_action()
    # print(selected_node.parent_action)
    # game.getTabuleiro().deslizar(selected_node.parent_action)
    # game.getTabuleiro().printTabuleiro()
    #
    # game.setRodada(15)
    # root = MonteCarloTreeSearchNode(game)
    # selected_node = root.best_action()
    # print(selected_node.parent_action)
    # game.getTabuleiro().deslizar(selected_node.parent_action)
    # game.getTabuleiro().printTabuleiro()

    gameCaia = Game(Tabuleiro())
    gameCaia.setRodada(1)
    for i in range(1000):
        print('Rodada: ', gameCaia.getRodada())
        tabuleiro = Tabuleiro(gameCaia.getTabuleiro().getDimensao(), False)
        copiaMatriz = gameCaia.getTabuleiro().getCopiaDaMatriz()
        tabuleiro.setMatrizNos(copiaMatriz)
        gameCopia = Game(tabuleiro)
        gameCopia.setRodada(gameCaia.getRodada())
        root = MonteCarloTreeSearchNode(gameCopia)

        selected_node = root.best_action()
        if selected_node.parent_action not in MOVIMENTOS_DESLIZES:
            gameCaia.getTabuleiro().inserirNoPorCoordenada(selected_node.parent_action, VALOR_INICIAL_POR_RODADA,
                                                           gameCaia.getAcaoPorRodada())
        else:
            print(selected_node.parent_action)
            gameCaia.getTabuleiro().deslizar(selected_node.parent_action)

        gameCaia.getTabuleiro().printTabuleiro()
        print('Score tabuleiro: ', gameCaia.getTabuleiro().getScoreTabuleiro())
        gameCaia.calcularScoreJogo()
        gameCaia.setRodada(gameCaia.getRodada() + 1)
    print('Score maximo do jogo: ', gameCaia.getScoreJogo())

if __name__ == "__main__":
    # runCaia()
    runLocal()
