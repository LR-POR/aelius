#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Aelius Brazilian Portuguese POS-Tagger and Corpus Annotation Tool
#
# Copyright (C) 2010-2013 Leonel F. de Alencar
# Author: Leonel F. de Alencar <leonel.de.alencar@ufc.br>
#          
# URL: <http://sourceforge.net/projects/aelius/>
# For license information, see LICENSE.TXT
#
# $Id: AnotaCorpus.py $

"""Anota sentenças enquanto listas de tokens unicode ou arquivos de texto em utf-8, utilizando os toquenizadores e etiquetadores morfossintáticos especificados. Para anotar um texto de um arquivo, consultar documentação da função AnotaCorpus.anota_texto. Exemplo de toquenização e etiquetagem de uma sentença:

>>> from Aelius.Extras import carrega
>>> from Aelius import Toqueniza, AnotaCorpus
>>> h=carrega('AeliusHunPos')
>>> b=carrega('AeliusBRUBT.pkl')
>>> lx=carrega('lxtagger')
>>> tokens1=Toqueniza.TOK_PORT.tokenize(AnotaCorpus.EXEMPLO)
>>> tokens2=Toqueniza.TOK_PORT_LX2.tokenize(AnotaCorpus.EXEMPLO)
>>> AnotaCorpus.anota_sentencas([tokens1],b)
[[(u'Os', u'D-P'), (u'candidatos', u'N-P'), (u'classific\xe1veis', u'ADJ-G-P'), (u'dos', u'P+D-P'), (u'cursos', u'N-P'), (u'de', u'P'), (u'Sistemas', u'NPR-P'), (u'de', u'P'), (u'Informa\xe7\xe3o', u'NPR'), (u'poder\xe3o', u'VB-R'), (u'ocupar', u'VB'), (u'as', u'D-F-P'), (u'vagas', u'ADJ-F-P'), (u'remanescentes', u'ADJ-G-P'), (u'do', u'P+D'), (u'Curso', u'NPR'), (u'de', u'P'), (u'Engenharia', u'NPR'), (u'de', u'P'), (u'Software', u'NPR'), (u'.', u'.')]]
>>> AnotaCorpus.anota_sentencas([tokens1],h,'hunpos')
[[(u'Os', 'D-P'), (u'candidatos', 'N-P'), (u'classific\xe1veis', 'ADJ-G-P'), (u'dos', 'P+D-P'), (u'cursos', 'N-P'), (u'de', 'P'), (u'Sistemas', 'NPR'), (u'de', 'P'), (u'Informa\xe7\xe3o', 'NPR'), (u'poder\xe3o', 'VB-R'), (u'ocupar', 'VB'), (u'as', 'D-F-P'), (u'vagas', 'ADJ-F-P'), (u'remanescentes', 'N-P'), (u'do', 'P+D'), (u'Curso', 'NPR'), (u'de', 'P'), (u'Engenharia', 'NPR'), (u'de', 'P'), (u'Software', 'NPR'), (u'.', '.')]]
>>> AnotaCorpus.anota_sentencas([tokens2],lx,'mxpost')
[[(u'Os', u'DA'), (u'candidatos', u'CN'), (u'classific\xe1veis', u'ADJ'), (u'de', u'PREP'), (u'os', u'DA'), (u'cursos', u'CN'), (u'de', u'PREP'), (u'Sistemas', u'PNM'), (u'de', u'PREP'), (u'Informa\xe7\xe3o', u'PNM'), (u'poder\xe3o', u'V'), (u'ocupar', u'INF'), (u'as', u'DA'), (u'vagas', u'CN'), (u'remanescentes', u'ADJ'), (u'de', u'PREP'), (u'o', u'DA'), (u'Curso', u'PNM'), (u'de', u'PREP'), (u'Engenharia', u'PNM'), (u'de', u'PREP'), (u'Software', u'PNM'), (u'.', u'PNT')]]

"""

import os,sys,nltk
from cPickle import load
try:
    	import xml.etree.cElementTree as ET
except ImportError:
    	import xml.etree.ElementTree as ET
#from Aelius.Extras import carrega
from Extras import carrega
from ProcessaNomesProprios import *
from ExpandeContracoes import expande_contracoes
from Toqueniza import PUNKT,TOK_PORT
from MXPOST import MXPOSTTagger
from openNLPJava import openNLPTagger

COMMENT=" TEI P5 header based on template created with EditiX http://www.editix.com/"
TEI=carrega("template.xml")
EXEMPLO="Os candidatos classificáveis dos cursos de Sistemas de Informação poderão ocupar as vagas remanescentes do Curso de Engenharia de Software.".decode("utf-8")
# Extraído da seguinte fonte:

# UFC convoca os classificáveis do Vestibular 2010. Disponível em: 
# <http://noticias.universia.com.br/destaque/noticia/2010/02/17/411825/
# fc-convoca-os-classificaveis-do-vestibular-2010.html> 
# Acesso em: 17/05/2011.

# A seguinte variável permite expandir contrações para obter maior
# acurácia com o LXTagger:
# EXPANDE_CONTRACOES=True

TAGGER=carrega("AeliusBRUBT.pkl")
    
# A seguinte variável global permite definir um
# infixo para arquivos anotados; caso essa variável
# permaneça com cadeia vazia como valor, o infixo é dado
# pela arquitetura do etiquetador:
INFIXO=""

USUARIO= os.path.expanduser("~")

HUNPOS=carrega("AeliusHunPos")

DESTINO="."


# O AeliusRUBT, usado como parte do procedimento
# de expansão de contrações, é mais rápido que o AeliusBRUBT,
# embora menos preciso:
TAGGER2=carrega("AeliusRUBT.pkl")


def toqueniza_contracoes(sentencas):
    """Esta função primeiro anota as sentenças com o TAGGER2, para depois utilizar seu output para separar as contrações.
    
>>> tokens1=AnotaCorpus.TOK_PORT.tokenize(AnotaCorpus.EXEMPLO)
>>> tokens1
[u'Os', u'candidatos', u'classific\xe1veis', u'dos', u'cursos', u'de', u'Sistemas', u'de', u'Informa\xe7\xe3o', u'poder\xe3o', u'ocupar', u'as', u'vagas', u'remanescentes', u'do', u'Curso', u'de', u'Engenharia', u'de', u'Software', u'.']
>>> AnotaCorpus.toqueniza_contracoes([tokens1])
[[u'Os', u'candidatos', u'classific\xe1veis', u'de', u'os', u'cursos', u'de', u'Sistemas', u'de', u'Informa\xe7\xe3o', u'poder\xe3o', u'ocupar', u'as', u'vagas', u'remanescentes', u'de', u'o', u'Curso', u'de', u'Engenharia', u'de', u'Software', u'.']]
>>> 
    """
    etiquetadas=_anota_sentencas_nltk(sentencas,TAGGER2)
    sents=[expande_contracoes(sent) for sent in etiquetadas]
    #print sents[0]
    #type (sents[0][0][0])
    return [nltk.tag.untag(sent) for sent in sents]    

# as duas funções seguintes representam uma modularização do programa
# e devem substituir partes de funções deste módulo e do módulo Avalia
def codifica_sentencas(sentencas):
    """Toma unicode como input e retorna string.
    """
    lista_sentencas=[]
    for sent in sentencas:
	cols=[]
	for w in sent:
		cols.append(w.encode("utf-8"))
	lista_sentencas.append(cols)
    return lista_sentencas

def decodifica_sentencas(sentencas):
    """Toma string como input e retorna unicode.
    """
    lista_sentencas=[]
    for sent in sentencas:
	cols=[]
	for w in sent:
		cols.append(w.decode("utf-8"))
	lista_sentencas.append(cols)
    return lista_sentencas

def codifica_sentencas_anotadas(sentencas_anotadas):
    lista_codificada=[]
    for sent in sentencas_anotadas:
        cols=[]
	for w,t in sent:
            #print w,t # teste aqui
            cols.append((w.encode("utf-8"),t.encode("utf-8")))
        lista_codificada.append(cols)
    return lista_codificada

def codifica_paragrafos_anotados(paragrafos_anotados):
    lista_codificada=[]
    for para in paragrafos_anotados:
        lista_codificada.append(codifica_sentencas_anotadas(para))
    return lista_codificada

def decodifica_sentencas_anotadas(sentencas_anotadas):
    lista_codificada=[]
    for sent in sentencas_anotadas:
        cols=[]
	for w,t in sent:
		cols.append((w.decode("utf-8"),t.decode("utf-8")))
        lista_codificada.append(cols)
    return lista_codificada

def extrai_corpus(arquivos,raiz=".",
                   toquenizador_sentencial= PUNKT,
                   #toquenizador_sentencial= REGEXP,
                   toquenizador_vocabular=TOK_PORT,
                   codificacao="utf-8"):

    """Retorna um corpus no formato do NLTK a partir de um arquivo de texto puro sem anotações. O texto é segmentado em palavras com base na expressão regular dada como argumento de nltk.RegexpTokenizer(), que retorna toquenizador armazenado na variável global em TOK_PORT. A segmentação em sentenças ocorre a cada quebra de linha. Em textos extraídos da WWW geralmente não há coincidência entre quebra de linha e final de sentença, o que torna necessária a definição de um outro toquenizador, o que é feito na função main, onde se utiliza o nltk.data.load('tokenizers/punkt/portuguese.pickle'). Assume-se que a codificação do texto-fonte é utf-8."""

    return nltk.corpus.PlaintextCorpusReader(raiz,
                                             arquivos,
                                             sent_tokenizer=toquenizador_sentencial,
                                             word_tokenizer=toquenizador_vocabular,
                                             encoding=codificacao)

def abre_etiquetador(modelo,arquitetura="nltk"):
    """Retorna etiquetador a partir do modelo e arquitetura especificados. O parâmetro 'arquitetura' tem como default 'nltk' e pode assumir também um dos seguintes valores: 'hunpos', 'stanford', 'mxpost' ou 'opennlp'. Nesse último caso, é construída e retornada instância de etiquetador de um desses tipos, invocando o construtor das classes HunposTagger, StanfordTagger e MXPOSTTagger, respectivamente. A codificação dos modelos deve ser utf-8. Caso a arquitetura seja nltk, assume-se que se trata de instância de etiquetador do NLTK armazenada em formato binário (extensão do arquivo '.pkl' ou '.pickle', por exemplo), sendo retornada instância de etiquetador do NLTK armazenada em formato binário."""
    a=arquitetura.lower()
    if a == "nltk":
        f=open(modelo,"rb")
        etiquetador=load(f)
        f.close()
        return etiquetador
    elif a =="hunpos":
        return nltk.tag.HunposTagger(modelo,encoding="utf-8")
    elif a =="stanford":
        return nltk.tag.StanfordTagger(modelo,encoding="utf-8")
    elif a =="mxpost":
        return MXPOSTTagger(modelo,encoding="utf-8")
    elif a =="opennlp":
        return openNLPTagger(modelo,encoding="utf-8")
    else:
        print "Valor inválido para o parâmetro arquitetura: %s" % arquitetura
    
def _anota_sentencas_nltk(sents,modelo):
    """Recebe uma lista de sentenças, onde cada sentença é uma lista de tokens em unicode,
    e retorna uma lista de sentenças etiquetadas conforme o modelo dado como parâmetro da função.
    Esse modelo deve ser um etiquetador de arquitetura NLTK. A função retorna uma lista de listas 
    de pares (w,t), onde w e t representam, respectivamente, uma palavra e a sua etiqueta, ambas em unicode.
    """
    # Futuramente, permitir a sepação de contrações.

    #minusculiza_nao_nomes_proprios(sents)
    sents=minusculiza_nao_nomes_proprios(sents)
    codificadas=codifica_sentencas(sents)
    etiquetador=abre_etiquetador(modelo,arquitetura="nltk")
    etiquetadas=etiquetador.batch_tag(codificadas)
    etiquetadas=decodifica_sentencas_anotadas(etiquetadas)
    maiusculiza_inicio(etiquetadas)
    return etiquetadas


def anota_sentencas(sents,modelo,arquitetura="nltk",separacao_contracoes=False):
    '''A partir de uma lista de sentenças (cada sentença constituindo, por sua vez, uma lista de palavras), retorna uma lista de sentenças anotadas pelo etiquetador especificado nos parâmetros modelo e arquitetura (ver documentação da função abre_etiquetador). Cada sentença anotada é uma lista de duplas (w,t), onde w é uma palavra e t, uma etiqueta.'''
    if arquitetura == "nltk":
        return _anota_sentencas_nltk(sents,modelo)

    #minusculiza palavras exceto as que ocorrem com maiúscula em posição não inicial
    #minusculiza_nao_nomes_proprios(sents)
    sents=minusculiza_nao_nomes_proprios(sents)
    etiquetador=abre_etiquetador(modelo,arquitetura)
    if separacao_contracoes:
        sents=toqueniza_contracoes(sents)
    etiquetadas=etiquetador.batch_tag(sents)
    if arquitetura=="stanford":
        lista_de_sentencas=[]
        for sent in etiquetadas:
            lista_de_sentencas.append([nltk.tag.util.str2tuple(wt[0]) for wt in sent])
        etiquetadas=lista_de_sentencas
    maiusculiza_inicio(etiquetadas)
    return etiquetadas
    
    
def anota_paragrafos(paras,modelo,arquitetura,separacao_contracoes):
    paragrafos=[]
    for paragrafo in paras:
        paragrafos.append(anota_sentencas(
            paragrafo,modelo,arquitetura,separacao_contracoes))
    return paragrafos

# esta função foi substituída por várias funções de
# escrita de corpus em arquivo (ver infra)
def escreve_corpus(lista_de_sentencas,nome):
    """A partir de lista de sentenças anotadas, onde cada sentença é uma lista de pares ordenados do tipo de ('palavra','N'), escreve corpus em arquivo de texto 'nome' em que os tokens são etiquetados da forma canônica palavra/N."""
    #f=open(os.path.join(USUARIO,nome),"w")
    f=open(nome,"w") # salva por defeito no diretório de trabalho
    c=1 # inicialização de um contador de palavras
    for sentenca in lista_de_sentencas:
        for palavra in sentenca:
            f.write("%s/%s<%d> " % (palavra[0],
                        palavra[1], c ) )
            c+=1
        f.write("\n")
        f.write("\n====================\n") # recurso para fase de teste
    f.close()

def maiusculiza_inicio(lista_de_sentencas):
    '''Maiusculiza as palavras minúsculas no início de sentença.
'''
    #print lista_de_sentencas # teste
    for indice in range(len(lista_de_sentencas)):
        palavras,etiquetas= separa_palavras_de_etiquetas(lista_de_sentencas[indice])
        palavras=maiusculiza_inicio_de_sentenca(palavras)
        lista_de_sentencas[indice]=zip(palavras,etiquetas)

def formata_paragrafos(paras):
    '''Maiusculiza o início de cada sentença do parágrafo.
'''
    paragrafos=[]
    for p in paras:
        maiusculiza_inicio(p)
    

def escreve_formato_nltk(paras,nome,desenvolvimento=False):
    separa_linhas="\n"
    separa_paragrafos="\n\n"
    c=1 # inicialização de um contador de palavras
    contador=""

    # recurso para fase de teste
    if desenvolvimento:
        separa_linhas="\n---------------\n"
        separa_paragrafos="\n====================\n"
        
    f=open(os.path.join(DESTINO,nome),"w")
    
    for p in paras: # posteriormente, criar duas funções diferentes, uma com contador e a outra sem, para evitar checar condição a cada palavra
        for sentenca in p:
            for palavra,etiqueta in sentenca:
                if desenvolvimento: 
                    contador="<%s>" % str(c)
                    c+=1
                    f.write("%s/%s%s " % (palavra,etiqueta, contador) )
                else:
                    f.write("%s/%s " % (palavra,etiqueta) )
            f.write(separa_linhas)
        f.write(separa_paragrafos)
    f.close()

def constroi_xml(paragrafos_anotados,capitulo=1):
	tree=ET.parse(TEI)
	root=tree.getroot()
	root.insert(0,ET.Comment(COMMENT))
	body=tree.getiterator("body")[0]
	div=ET.SubElement(body,"div",type="chap",n="%d" % capitulo)
	t,s,p=1,1,1
	for para in paragrafos_anotados:
		elemento_p=ET.SubElement(div,'p',n="%d" % p)
		p+=1
		for sent in para:
			elemento_s=ET.SubElement(elemento_p,'s',n="%d" % s)
			s+=1
			for palavra,etiqueta in sent:
				elemento_w=ET.SubElement(elemento_s,'w',type=etiqueta)
				elemento_w.text=palavra
				elemento_w.set("xml:id","w%d" % t)
				t+=1
	return tree
		
def escreve_formato_xml(paragrafos_anotados,nome):
	element_tree=constroi_xml(paragrafos_anotados)
	element_tree.write(nome,
	"UTF-8",
	xml_declaration='<?xml version="1.0" encoding="UTF-8"?>')

def _escreve_formato_xml(paras,nome,capitulo="1"):
    """Versão antiga da função escreve_formato_xml()
"""
    # inicialização de contadores para palavras, sentenças e parágrafos
    c,s,p=1,1,1
    f=open(os.path.join(DESTINO,nome),"w")
    f.write('<div type="chap" n="%s">' % capitulo)
    for para in paras:
        f.write('<p n="%d">' % p)
        for sentenca in para:
            f.write('<s n="%d">' %s)
            for palavra in sentenca:
                f.write('<w xml:id="w%d" type="%s">%s</w> ' % (c, palavra[1],palavra[0] ) )
                c+=1
            f.write('</s>')
            s+=1
        f.write('</p>')
        p+=1
    f.write('</div>')
    f.close()


def anota_texto(arquivo,
                modelo=TAGGER,
                arquitetura="nltk",
                toquenizador=TOK_PORT,
                raiz=".",
                codificacao="utf-8",
                formato=None,
                separacao_contracoes=False):
    """Anota arquivo e salva o resultado, no atual diretório de trabalho,
em arquivo com extensão .INFIXO.txt (onde INFIXO é o valor dessa variável
global, se definida como cadeia não vazia, ou, caso contrário, o valor do
parâmetro arquitetura). É possível especificar um dos três formatos da
anotação: nltk (default), aelius e xml.
Exemplo de anotação de um texto com o etiquetador default AeliusBRUBT.pkl:

>>> import os
>>> from Aelius import AnotaCorpus
>>> from Aelius.Extras import carrega
>>> raiz,nome=os.path.split(carrega('exemplo.txt'))
>>> AnotaCorpus.INFIXO=''
>>> AnotaCorpus.anota_texto(nome,raiz=raiz)
Arquivo anotado:
exemplo.nltk.txt
>>> AnotaCorpus.anota_texto(nome,raiz=raiz,formato='xml')
Arquivo anotado:
exemplo.nltk.xml
>>>

Outros exemplos:
>>> AnotaCorpus.INFIXO='rubt'
>>> AnotaCorpus.anota_texto(nome,AnotaCorpus.TAGGER2,raiz=raiz)
Arquivo anotado:
exemplo.rubt.txt
>>> AnotaCorpus.anota_texto(nome,AnotaCorpus.TAGGER2,raiz=raiz,formato='aelius')
Arquivo anotado:
exemplo.pos.aelius.txt
>>> h=carrega('AeliusHunPos')
>>> lx=carrega('lxtagger')
>>> m=carrega('AeliusHunPosMM')
>>> AnotaCorpus.INFIXO=""
>>> AnotaCorpus.anota_texto(nome,h,'hunpos',raiz=raiz)
Arquivo anotado:
exemplo.hunpos.txt
>>> AnotaCorpus.anota_texto(nome,lx,'mxpost',Toqueniza.TOK_PORT_LX2,raiz=raiz,formato='xml',separacao_contracoes=True)
Arquivo anotado:
exemplo.mxpost.xml
>>> AnotaCorpus.INFIXO='macmorpho'
>>> AnotaCorpus.anota_texto(nome,m,'hunpos',Toqueniza.TOK_PORT_MM,raiz=raiz,separacao_contracoes=True)
Arquivo anotado:
exemplo.macmorpho.txt
>>> s=carrega('AeliusStanfordMM')
>>> AnotaCorpus.INFIXO='stanford'
>>> AnotaCorpus.anota_texto(nome,s,'stanford',Toqueniza.TOK_PORT_MM,raiz=raiz,separacao_contracoes=True)
Arquivo anotado:
exemplo.stanford.txt
>>> AnotaCorpus.INFIXO='maxent'
>>> mx=carrega('AeliusMaxEnt')
>>> AnotaCorpus.anota_texto(nome,mx,'mxpost',raiz=raiz)
Arquivo anotado:
exemplo.maxent.txt
>>> 

    """

    nome_output=[]
    corpus=extrai_corpus(arquivo,
                         raiz=raiz,
                         toquenizador_vocabular=toquenizador,
                   codificacao=codificacao)
    paragrafos=corpus.paras()
    anotados=anota_paragrafos(paragrafos,modelo,arquitetura,separacao_contracoes)
    if formato != "xml":
    	anotados=codifica_paragrafos_anotados(anotados)
    # aqui: codificação dos parágrafos, para que possam ser gravados em arquivo
    #return anotados 
    if INFIXO:
        infixo=INFIXO
    else:
        infixo=arquitetura
    #formata_paragrafos(anotados) # linha a ser eliminada? 30.03.2011
    lista=arquivo.split(".txt")
    base_nome_input=lista[0]
    if formato:
        if formato == "aelius":
            nome_output.append("%s.pos.%s.txt" % (base_nome_input,formato))
            escreve_formato_nltk(anotados,nome_output[0],desenvolvimento=True)
        elif formato == "xml":
            nome_output.append("%s.%s.%s" % (base_nome_input,infixo,formato))
            escreve_formato_xml(anotados,nome_output[0])
        else:
            nome_output.append("%s.%s.txt" % (base_nome_input,infixo))
            escreve_formato_nltk(anotados,nome_output[0])
    else:
        nome_output.append("%s.%s.txt" % (base_nome_input,infixo))
        escreve_formato_nltk(anotados,nome_output[0])
    #print "Arquivo anotado:\n%s" % os.path.join(os.getcwd(),nome_output)
    print "Arquivo anotado:\n%s" % nome_output[0]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
