#!/usr/bin/python

import os

import mercado

ARQUIVO_MOD = 'olheiro.mod'
ARQUIVO_DAT = 'olheiro.dat'
GLPSOL_EXEC = 'glpsol -m %s -d %s' % (ARQUIVO_MOD, ARQUIVO_DAT)
LISTA_CONJUNTOS = ['S_Jogadores', 'S_Posicoes', 'S_Formacoes']
LISTA_PARAMETROS = ['P_Patrimonio', 'P_Preco', 'P_Media',
                    'Pe_Posicao', 'P_Quantidade']
DEFAULT = {'P_Patrimonio': 0.0, 'P_Preco': 0.0, 
           'P_Media': 0.0, 'P_Quantidade': 0.0}
FORMACOES = {
    '343': {
        'TEC': 1,
        'GOL': 1,
        'ZAG': 3,
        'MEI': 4,
        'ATA': 3,
        },
    '352': {
        'TEC': 1,
        'GOL': 1,
        'ZAG': 3,
        'MEI': 5,
        'ATA': 2,
        },
    '433': {
        'TEC': 1,
        'GOL': 1,
        'ZAG': 2,
        'LAT': 2,
        'MEI': 3,
        'ATA': 3,
        },
    '442': {
        'TEC': 1,
        'GOL': 1,
        'ZAG': 2,
        'LAT': 2,
        'MEI': 4,
        'ATA': 2,
        },
    '451': {
        'TEC': 1,
        'GOL': 1,
        'ZAG': 2,
        'LAT': 2,
        'MEI': 5,
        'ATA': 1,
        },
    }


def gravaConjunto(arq, nome, conteudo):
    '''Grava o conteudo de um conjunto no formato DAT.'''
    _conteudo = ' '.join(map(lambda z: str(z), conteudo))
    arq.write('set %s := %s;\n' % (nome, _conteudo))

def gravaParametro(arq, nome, conteudo, default_=None):
    '''Grava o conteudo de um parametro no formato DAT;
    o parametro que pode ou nao ter um valor
    default (argumento 'default_').'''
    
    arq.write('param %s ' % nome)
    if default_ is not None:
        arq.write('default %s ' % str(default_))
    arq.write(':= \n')
    
    for item in conteudo:
        arq.write('    ')
        for i in item:
            arq.write('%s ' % str(i))
        arq.write('\n')
    arq.write(';\n')

def identify(j):
    return ("'%s : %s'" % (j.apelido, j.clube.slug)).encode('iso-8859-1')

if __name__ == '__main__':
    cenario = mercado.busca_mercado()

    cenario.jogadores = [j for j in cenario.jogadores
                         if (j.status_id == 7 and
                             j.jogos >= 3)]

    data = {}

    data['S_Jogadores'] = [identify(j) for j in cenario.jogadores]
    data['S_Posicoes'] = list(set("'%s'" % j.posicao
                                  for j in cenario.jogadores))
    data['S_Formacoes'] = ["'%s'" % f for f in FORMACOES.keys()]

    data['P_Patrimonio'] = [(raw_input('Patrimonio: '),)]
    data['P_Preco'] = [(identify(j), j.preco) for j in cenario.jogadores]
    data['P_Media'] = [(identify(j), j.media) for j in cenario.jogadores]
    data['Pe_Posicao'] = [(identify(j), j.posicao) for j in cenario.jogadores]
    data['P_Quantidade'] = [
        ("'%s'" % f, "'%s'" % p, FORMACOES[f][p])
        for p in FORMACOES[f].keys()
        for f in FORMACOES.keys()]
    
    arq = open(ARQUIVO_DAT, 'w')
    for conj in LISTA_CONJUNTOS:
        gravaConjunto(arq, conj, data.get(conj, []))
    for param in LISTA_PARAMETROS:
        gravaParametro(arq, param, data.get(param, []),
                       DEFAULT.get(param))
    arq.close()

    output = os.popen(GLPSOL_EXEC)

    skip = True
    for linha in output:
        if ('Model has been successfully '
            'processed') in linha:
            break
        if 'Resultado da otimizacao' in linha:
            skip = False
        if not skip:
            print linha,
