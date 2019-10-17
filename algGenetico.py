import random
import math
import sys
import copy

class No:
    valor = None
    pai = None
    direito = None
    esquerdo = None

    def __init__(self, valor, pai = None):
        self.valor = valor
        self.pai = pai

class Individuo:
    raiz = None
    def __init__(self, raiz:No):
        self.raiz = raiz
        self._ordem_calculo = []
        self.resultado = 99999
        self.pontos = []

    def altura(self, raiz = None):
        if raiz == None:
            raiz = self.raiz

        if raiz == None:
            return -1
        else:
            alturaDireita = -1
            alturaEsquerda = -1
            if raiz.direito:
                alturaDireita = self.altura(raiz.direito)
            if raiz.esquerdo:
                alturaEsquerda = self.altura(raiz.esquerdo)
            if alturaEsquerda < alturaDireita:
                return alturaDireita + 1
            else:
                return alturaEsquerda + 1

    def pos_ordem(self, no:No):
        if not no:
            return
        self.pos_ordem(no.esquerdo)
        self._ordem_calculo.append(no.valor)
        self.pos_ordem(no.direito)

    def _resultado_funcao(self, valor_x):
        self._ordem_calculo = []
        self.pos_ordem(self.raiz)
        formula = ''
        for i in self._ordem_calculo:
            if i == 'x':
                i = valor_x
            formula = formula + ' ' + str(i)
        try:
            return eval(formula)
        except ZeroDivisionError:
            return 9999
        except:
            pass

    def fitness(self, altura_maxima):

        if self.altura() > altura_maxima:
            self.resultado = 99999
        else:
            y = [0.67, 2.00, 4.00, 6.67, 10.00, 14.00, 18.67, 24.00, 30.00, 36.67]
            somatorio = 0
            for i in range(1, 11):
                resultado_x = self._resultado_funcao(i)
                if (len(self.pontos)<10):
                    self.pontos.append(resultado_x)
                resultado_pacial = y[i-1] - resultado_x
                somatorio = (resultado_pacial * resultado_pacial) + somatorio
            resultado_comparacao = math.sqrt(somatorio)
            self.resultado = resultado_comparacao

    def formula(self):
        self._ordem_calculo = []
        self.pos_ordem(self.raiz)
        formula = ''
        for i in self._ordem_calculo:
            formula = formula + ' ' + str(i)
        return formula


class AlgoritmoGenetico:

    def __init__(self):
        self.operadores = ['+', '-', '*', '%']
        self.termos = ['x', -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
        self.possiveis_valores = self.operadores + self.termos
        #########################
        self.melhor_individuo = None #type Individuo

    def gerar_subarvore(self, raiz):
        v1 = random.choice(self.possiveis_valores)
        noEsquerdo = No(v1, raiz)
        raiz.esquerdo = noEsquerdo

        if self.operadores.count(noEsquerdo.valor):
            self.gerar_subarvore(raiz.esquerdo)
        v2 = random.choice(self.possiveis_valores)
        noDireito = No(v2, raiz)
        raiz.direito = noDireito

        if self.operadores.count(noDireito.valor):
            self.gerar_subarvore(raiz.direito)
        return raiz

    def gerar_individuo(self):
        operador = random.choice(self.operadores)
        raiz = No(operador)
        individuo = Individuo(raiz)
        self.gerar_subarvore(individuo.raiz)
        individuo.altura()
        individuo.fitness(self.altura_maxima)
        return individuo

    def gerar_populacao_inicial(self):
        individuals = []
        individuo = self.gerar_individuo()
        if individuo.altura() <= self.altura_maxima:
            individuals.append(individuo)

        while len(individuals) < self.tamanho_inicial_populacao:
            individuo = self.gerar_individuo()
            if individuo.altura() <= self.altura_maxima:
                individuals.append(individuo)
        return individuals

    def ordenacao_populacao(self, populacao:list):
        for item in range(len(populacao) - 1, 0, -1):
            for i in range(item):
                if populacao[i].resultado > populacao[i + 1].resultado:
                    temp = populacao[i]
                    populacao[i] = populacao[i + 1]
                    populacao[i + 1] = temp
        return populacao

    def selecao_elitista(self, populacao:list):
        populacao = self.ordenacao_populacao(populacao)
        tamanho_populacao = len(populacao)
        corte = int(tamanho_populacao - (tamanho_populacao * self.porcentagem_reducao_populacional) / 100)
        return populacao[:corte]

    def tree2list(self, raiz:No, lista:list):
        lista.append(raiz)
        if raiz.direito:
            lista = self.tree2list(raiz.direito, lista)
        if raiz.esquerdo:
            lista = self.tree2list(raiz.esquerdo, lista)
        return lista

    def permutacao(self, individual1:Individuo, individual2:Individuo):
        novo_individual1 = copy.deepcopy(individual1)
        novo_individual2 = copy.deepcopy(individual2)
        lista_nos1 = self.tree2list(novo_individual1.raiz, [])
        ponto_troca1 = random.randint(1, len(lista_nos1)-1)
        lista_nos2 = self.tree2list(novo_individual2.raiz, [])
        ponto_troca2 = random.randint(1, len(lista_nos2)-1)
        no_itercambio1 = lista_nos1[ponto_troca1] # type:No
        no_itercambio2 = lista_nos2[ponto_troca2] # type:No
        pai_aux = no_itercambio1.pai
        no_itercambio1.pai = no_itercambio2.pai
        no_itercambio2.pai = pai_aux

        if no_itercambio1.pai.esquerdo == no_itercambio2:
            no_itercambio1.pai.esquerdo = no_itercambio1
        else:
            no_itercambio1.pai.direito = no_itercambio1

        if no_itercambio2.pai.esquerdo == no_itercambio1:
            no_itercambio2.pai.esquerdo = no_itercambio2
        else:
            no_itercambio2.pai.direito = no_itercambio2

        novo_individual1.altura()
        novo_individual1.fitness(self.altura_maxima)
        novo_individual2.altura()
        novo_individual2.fitness(self.altura_maxima)
        return [novo_individual1, novo_individual2]

    def recombinacao_populacao(self, populacao:list, percentual_recombinacao:int):
        tamanho_populacao = len(populacao)
        num_recombinacao = int((tamanho_populacao*percentual_recombinacao)/100)
        posicoes_aleatorias = list(range(tamanho_populacao))
        random.shuffle(posicoes_aleatorias)
        novos_individuos = []
        for i in range(int(num_recombinacao / 2)):
            individual1 = populacao[posicoes_aleatorias[i]]
            individual2 = populacao[posicoes_aleatorias[(num_recombinacao - 1) - i]]
            novos_individuos = novos_individuos + self.permutacao(individual1, individual2)
        return novos_individuos

    def mutacao(self, populacao):
        tamanho_populacao = len(populacao)
        num_mutacao = int(tamanho_populacao - (tamanho_populacao*self.percentual_mutacao)/100)
        for i in range(0, num_mutacao):
            indece = random.randint(0, (tamanho_populacao-1))
            novo_individual1 = populacao[indece]
            lista_nos1 = self.tree2list(novo_individual1.raiz, [])
            ponto_troca1 = random.randint(1, len(lista_nos1) - 1)
            no_itercambio1 = lista_nos1[ponto_troca1]  # type:No
            operador = random.choice(self.operadores)
            raiz = No(operador)
            novo_individual_gerado = Individuo(raiz)
            self.gerar_subarvore(novo_individual_gerado.raiz)
            pai_aux = no_itercambio1.pai
            novo_individual_gerado.raiz.pai = pai_aux
            if no_itercambio1.pai.esquerdo == pai_aux:
                no_itercambio1.pai.esquerdo = novo_individual_gerado.raiz
            else:
                no_itercambio1.pai.direito = novo_individual_gerado.raiz
            novo_individual1.altura()
            novo_individual1.fitness(self.altura_maxima)
        return populacao

    def tecnica_selecao_elitista(self, populacao_inicial:list):
        gen = 1
        populacao = populacao_inicial
        self.melhor_individuo = populacao[0]
        melhores = []

        while gen <= self.num_max_geracoes and self.melhor_individuo.resultado != 0:
            populacao = self.selecao_elitista(populacao)
            for i in populacao:
                if self.melhor_individuo.resultado > i.resultado:
                    self.melhor_individuo = copy.deepcopy(i)
            melhores.append(self.melhor_individuo)
            print (f'Distancia: {round(self.melhor_individuo.resultado,3)} ({self.melhor_individuo.formula()}) Altura: {self.melhor_individuo.altura()}')

            populacao = self.mutacao(populacao)
            novos_individuos = self.recombinacao_populacao(populacao, self.percentual_recombinacao)
            populacao = populacao + novos_individuos
            gen = gen + 1
        print ('--- Fim ---')
        for geracao,individuo in enumerate(melhores):
            print (f'Gen: {geracao+1} | Melhor: {individuo.resultado} ({individuo.formula()})')
            print(f'Pontos: {individuo.pontos}')


ag = AlgoritmoGenetico()

ag.tamanho_inicial_populacao = 5000
ag.altura_maxima = 4
ag.num_max_geracoes = 10
ag.percentual_mutacao = 50
ag.percentual_recombinacao = 100
ag.porcentagem_reducao_populacional = 50

populacao_inicial = ag.gerar_populacao_inicial()
ag.tecnica_selecao_elitista(populacao_inicial)
