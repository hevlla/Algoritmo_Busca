import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

grafo = nx.Graph()
cidades = open('./info_cidades/arestas.csv')

# Carrega as arestas
for linha in cidades:
    info_cidades = linha.split(",")
    info_cidades[2] = info_cidades[2].replace("\n", "")
    grafo.add_edge(info_cidades[0], info_cidades[1], weight=float(info_cidades[2]))

# Carrega a heurística
euristica = pd.read_csv("./info_cidades/heuristica.csv", header=0, index_col=0)

def Caminho_dfs(grafo, partida, objetivo, caminho=None):
    """ Algoritmo de busca em profundidade (Depth-first search)
    Retorna um generator contendo todos os caminhos encontados na busca"""
    if caminho is None:
        caminho = [partida]
    if partida == objetivo:
        yield caminho
    for next in set([i for i in grafo.neighbors(partida)]) - set(caminho):
        yield from Caminho_dfs(grafo, next, objetivo, caminho + [next])


def Caminho_brfs(grafo, partida, objetivo):
    """ Algoritmo de busca em largura (BrFS - Breadth-first search)
        Retorna um generator contendo todos os caminhos encontados na busca"""
    fila = [(partida, [partida])]
    while fila:
        (vertice, caminho) = fila.pop(0)
        for next in set([i for i in grafo.neighbors(vertice)]) - set(caminho):
            if next == objetivo:
                yield caminho + [next]
            else:
                fila.append((next, caminho + [next]))


def pinta_arestas(grafo, pos, route, color):
    """Função auxiliar que pinta as arestas e os pontos de início e destino no grafo"""
    arestas = [(route[n], route[n + 1]) for n in range(len(route) - 1)]
    nx.draw_networkx_edges(grafo, pos=pos, edgelist=arestas, edge_color=color, width=2.0)
    nx.draw_networkx_nodes(grafo, pos, nodelist=[route[0], route[-1]], node_size=20, node_color='red')


def aresta_menor_peso(grafo, no, visitado=None):
    """Seleciona qual o destino da aresta de menor peso"""
    if not visitado:
        visitado = [no]
    else:
        if no not in visitado:
            visitado.append(no)

    adj = set(grafo[no]) - set(visitado)
    min = list(adj)[0]

    for i in adj:
        if grafo[no][i]['weight'] < grafo[no][min]['weight']:
            min = i

    return min


def menor_peso_heuristica(grafo, no, objetivo, visitado=None):
    """Seleciona o destino com menor peso levando em conta a heurística e o peso da aresta.
    A heurística escolhida foi a distância em linha reta entre as cidades"""
    if not visitado:
        visitado = [no]
    else:
        if no not in visitado:
            visitado.append(no)
    adj = list(set(grafo[no]) - set(visitado))
    if objetivo in adj:
        return objetivo
    min = adj[0]

    for i in adj[1:]:
        heuristica = euristica[objetivo][i]
        if np.isnan(heuristica):
            heuristica = euristica[i][objetivo]

        heu_min = euristica[objetivo][min]
        if np.isnan(heu_min):
            heu_min = euristica[min][objetivo]

        if grafo[no][i]['weight'] + heuristica < grafo[no][min]['weight'] + heu_min:
            min = i

    return min


def a_estrela(grafo, partida, objetivo, caminho=None):
    """Algoritmo de busca A*
    Retorna o caminho calculado de acordo com o menor peso da aresta + heurística até o destino"""
    if caminho is None:
        caminho = [partida]
    if partida == objetivo:
        return caminho

    prox = menor_peso_heuristica(grafo, partida, objetivo, caminho)
    return a_estrela(grafo, prox, objetivo, caminho + [prox])


def obtem_posicionamento(grafo):
    """Carrega o posicionamento das arestas caso o mesmo exista,
    caso contrário, é aplicado o layout spring do NetworkX"""
    try:
        coord = open('./info_cidades/coordenadas.csv')
        pos = {}
        for linha in coord:
            linha.replace("\n", "")
            linha = linha.split(",")
            pos[linha[0]] = (float(linha[1]), float(linha[2]))
    except:
        pos = nx.spring_layout(grafo)
    return pos


if __name__ == '__main__':
    while True:

        partida = input("Origem: \n").lower().capitalize()
        if partida not in grafo.nodes:
            print("{} não está presente no mapa".format(partida))
            continue
        objetivo = input("Destino: \n").lower().capitalize()
        if objetivo not in grafo.nodes:
            print("{} não está presente no mapa".format(objetivo))
            continue

        escolha = int(
            input("Escolha o tipo de algoritmo: \n1 - Busca em largura\n2 - Busca em Profundidade\n3 - A*\n"))
        if escolha == 1:
            plt.title("Busca em largura\n{} para {}".format(partida, objetivo))
            res = next(Caminho_brfs(grafo, partida, objetivo))
        elif escolha == 2:
            plt.title("Busca em profundidade\n{} para {}".format(partida, objetivo))
            res = next(Caminho_dfs(grafo, partida, objetivo))
        elif escolha == 3:
            plt.title("Busca em A*\n{} para {}".format(partida, objetivo))
            res = a_estrela(grafo, partida, objetivo)
        else:
            break

        pos = obtem_posicionamento(grafo)
        nx.draw_networkx_nodes(grafo, pos, node_size= 20, node_color= 'red')
        nx.draw_networkx_edges(grafo, pos)
        nx.draw_networkx_labels(grafo, pos)
        pinta_arestas(grafo, pos, res, 'cyan')
        plt.show()
