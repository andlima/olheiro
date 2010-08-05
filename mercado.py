#!/usr/bin/python

# Autor: Andre Lima

'''
Este modulo eh responsavel por obter e armazenar as informacoes relativas
ao cenario atual do mercado de jogadores e tecnicos do Cartola FC.

Ele disponibiliza o metodo busca_mercado(), que verifica se existe um dump
atual das informacoes; caso nao exista, ele tenta obter as informacoes e
salva-lo. A funcao retorna uma instancia da Classe cenario, que agrega
informacoes como clubes, jogadores e partidas da rodada atual.

Quando chamado diretamente, o modulo escreve as informacoes do cenario
construido num arquivo texto em formato tabulado.
'''

import itertools
import pickle
import bz2
import json
import time
from ConfigParser import ConfigParser

import mechanize


LOGIN_URL = 'https://loginfree.globo.com/login/438'
URL_MERCADO = ('http://cartolafc.globo.com/mercado/filtrar.json?'
               'page=%d&order_by=preco')
MERCADO_DUMP = 'mercado-%s.dump'
MERCADO_TXT= 'mercado.txt'
ARQUIVO_CONFIG = 'mercado.cfg'

def arquivo_mercado_atual():
    '''
    Retorna nome do arquivo que armazena o dump das informacoes
    de mercado relativas ao dia atual.
    '''

    return MERCADO_DUMP % time.strftime('%Y-%m-%d')


class Cenario:
    def __init__(self, mercado=None):
        self.clubes = []
        self.jogadores = []
        self.partidas = []
        if mercado:
            for item in mercado:
                self.jogadores.append(Jogador(item, self))
                self.add_partida(Partida(item))

    def get_clube_by_id(self, id_):
        candidates = [clube
                      for clube in self.clubes
                      if clube.id == id_]
        if candidates:
            return candidates[0]
        else:
            return None

    def get_partida_by_id(self, id_):
        candidates = [partida
                      for partida in self.partidas
                      if partida.id == id_]
        if candidates:
            return candidates[0]
        else:
            return None

    def add_clube(self, clube):
        if clube.id not in (x.id for x in self.clubes):
            self.clubes.append(clube)
        return self.get_clube_by_id(clube.id)

    def add_partida(self, partida):
        if partida.id not in (x.id for x in self.partidas):
            self.partidas.append(partida)
        return self.get_partida_by_id(partida.id)


class Clube:
    def __init__(self, data):
        self.id = data['id']
        self.abreviacao = data['abreviacao']
        self.mercado = data['mercado']
        self.nome = data['nome']
        self.slug = data['slug']

    def __repr__(self):
        return '<Clube %s, %s>' % (self.id,
                                   self.abreviacao)


class ScoutTable:
    SCOUTS = ['RB', 'FC', 'GC', 'CA', 'CV', 'SG', 'DD', 'DP', 'GS',
              'FS', 'PE', 'A', 'FT', 'FD', 'FF', 'G', 'I', 'PP']
    PONTUACAO = {'RB': 1.7, 'FC': -0.5, 'GC': -6, 'CA': -2, 'CV': -5,
                 'SG': 5, 'DD': 3, 'DP': 7, 'GS': -2, 'FS': 0.5,
                 'PE': -0.3, 'A': 5, 'FT': 3.5, 'FD': 1, 'FF': 0.7,
                 'G': 8, 'I': -0.5, 'PP': -3.5}

    def __init__(self, data):
        self.conteudo = {}
        for item in data:
            self.conteudo[item['nome']] = item['quantidade']

    def get_scout(self, scout):
        if scout in ScoutTable.SCOUTS:
            return self.conteudo.get(scout, 0)
        return None

    def pontuacao(self):
        soma = 0.0
        return soma

    def imprime(self):
        elementos = []
        for scout in ScoutTable.SCOUTS:
            elementos.append(str(self.get_scout(scout)))
        return '\t'.join(elementos)


class Partida:
    def __init__(self, data):
        self.id_clube_casa = data['partida_clube_casa']['id']
        self.id_clube_visitante = data['partida_clube_visitante']['id']
        self.quando = data['partida_data']
        self.id = (self.id_clube_casa,
                   self.id_clube_visitante,
                   self.quando)

    def __repr__(self):
        return '<Partida %s>' % std(self.id)


class Jogador:
    def __init__(self, data, cenario):
        self.id = data['id']
        self.apelido = data['apelido']
        clube = Clube(data['clube'])
        cenario.add_clube(clube)
        self.clube = clube
        self.status_id = data['status_id']
        self.posicao = data['posicao']['abreviacao']
        self.jogos = int(data['jogos'])
        self.preco = float(data['preco'])
        self.variacao = float(data['variacao'])
        self.media = float(data['media'])
        self.pontos = float(data['pontos'])
        self.scout = ScoutTable(data['scout'])

    def imprime(self):
        elementos = []
        elementos.append(self.clube.slug)
        elementos.append(self.posicao)
        elementos.append(self.apelido)
        elementos.append('%d' % self.jogos)
        elementos.append('%.2f' % self.preco)
        elementos.append('%.2f' % self.variacao)
        elementos.append('%.2f' % self.media)
        elementos.append('%.2f' % self.pontos)
        elementos.append(self.scout.imprime())
        return '\t'.join(elementos)

    def __repr__(self):
        return '<Jogador %s, %s, %s>' % (str(self.id),
                                         self.apelido.encode('iso-8859-1'),
                                         repr(self.clube))


def get_user_and_password():
    '''Busca por usuario e senha em um arquivo de configuracao.'''
    
    config = ConfigParser()

    if config.read(ARQUIVO_CONFIG):
        print 'Utilizando arquivo de configuracao "%s".' % ARQUIVO_CONFIG
        username = config.get('DEFAULT', 'username')
        compressed = eval(config.get('DEFAULT', 'compressed_password'))
        password = bz2.decompress(compressed)
    else:
        username = None
        password = None

    return username, password


def busca_mercado():
    '''Busca as informacoes de um cenario atual de mercado.'''
    
    paginas = []

    try:
        # Busca por dump do mercado atualizado.

        with open(arquivo_mercado_atual(), 'r') as f:
            paginas.extend(pickle.load(f))
        print 'Cache de mercado encontrado.'

    except IOError:
        # Caso nao ache o dump, faz download do site.

        print 'Cache de mercado nao encontrado...'

        br = mechanize.Browser()

        username, password = get_user_and_password()
        if not username:
            username = raw_input(' - Login: ')
        if not password:
            from getpass import getpass
            password = getpass(' - Senha: ')

        print 'Iniciando download das informacoes de mercado...'

        # Procedimento de login, utilizando mechanize.
        br.open(LOGIN_URL)
        br.select_form(nr=0)
        br['login-passaporte'] = username
        br['senha-passaporte'] = password

        form = list(br.forms())[0]
        form.click()

        r_login = br.submit()
        conteudo = r_login.get_data()

        # Faz download de todas as paginas de informacao de mercado
        # dos atletas e treinadores provaveis para a rodada seguinte.
        # As paginas estao no formato JSON.
        for n in itertools.count(1):
            r_mercado = br.open(URL_MERCADO % n)
            pagina = str(r_mercado.get_data())
            paginas.append(pagina)
            data = json.JSONDecoder().decode(pagina)
            if data['page']['atual'] == data['page']['total']:
                # Sai do loop apos obter a ultima pagina.
                break

        # Faz dump do mercado atualizado, com todas as paginas.
        f = open(arquivo_mercado_atual(), 'w')
        pickle.dump(paginas, f)
        f.close()


    mercado = []
    for pagina in paginas:
        data = json.JSONDecoder().decode(pagina)
        mercado.extend(data[u'atleta'])

    # Retorna um cenario com as informacoes atualizadas do mercado.
    return Cenario(mercado)


if __name__ == '__main__':
    cenario = busca_mercado()

    # Grava as informacoes dos jogadores de maneira tabelada.
    f = open(MERCADO_TXT, 'w')
    for jogador in cenario.jogadores:
        f.write(jogador.imprime().encode('iso-8859-1')+'\n')
    f.close()
