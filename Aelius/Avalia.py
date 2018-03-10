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
# $Id: Avalia.py $
"""Este módulo contém funções úteis para avaliação de etiquetadores morfossintáticos.
"""
import os
import nltk
from cPickle import dump
from AnotaCorpus import anota_sentencas,codifica_sentencas_anotadas
VERBOSE=False
LISTA_DE_ERROS=[]
USUARIO=os.path.expanduser("~")

def avalia(output,gold,tagged_words):
    """Output é a lista de sentenças anotadas automaticamente,
gold é a lista de sentenças anotadas por humano; tagged_words é a
quantidade de tokens anotados. Se o valor da variável global VERBOSE
for True, os erros são armazenados na variável global LISTA_DE_ERROS.
"""
    erros=0
    del LISTA_DE_ERROS[:]
    for m in range(len(output)):
        for n in range(len(output[m])):
            out=output[m][n]
            g=gold[m][n]
            if out[1] != g[1]: 
                erros+=1
# esta variável global, cujo valor é um booliano, determina o armazenamento ou não# dos erros
                if VERBOSE:
                    LISTA_DE_ERROS.append((out[0],out[1],g[0],g[1]))
    # os erros só poderão ser exibidos se tiverem sido armazenados nesta lista
    print "Total de erros: %d\nTotal de palavras:%d\nAcurácia:%f" % (erros,tagged_words,100-100.0/tagged_words*erros)

def exibe_erros(maximo=None):
    """Exibe os erros armazenados na variável global LISTA_DE_ERROS.
    """
    if LISTA_DE_ERROS:
        i=0
        print "Anotação automática\tAnotação humana\n"
        if maximo:
            limite=maximo
        else:
            limite=len(LISTA_DE_ERROS)
        while i < limite:
            w1,t1,w2,t2=LISTA_DE_ERROS[i]
            print "%s/%s\t%s/%s" % (w1,t1,w2,t2)
            i+=1
    else:
        print "Lista de erros vazia."

def grava_erros(arquivo):
    """Grava em arquivo os erros armazenados na variável global LISTA_DE_ERROS.
    """
    if LISTA_DE_ERROS:
        f=open(arquivo,"w")
        for w1,t1,w2,t2 in LISTA_DE_ERROS:
            f.write("%s\t%s\t%s\t%s\n" % (w1.encode("utf-8"),t1.encode("utf-8"),w2.encode("utf-8"),t2.encode("utf-8")))
        f.close()
    else:
        print "Lista de erros vazia."
        # luzia_gold.cap1.txt
def testa_etiquetador(modelo,arquitetura="nltk",raiz=".",ouro="luzia_gold\.cap\d+\.txt"):

    corpus=nltk.corpus.TaggedCorpusReader(raiz,ouro,
    				      sent_tokenizer=nltk.RegexpTokenizer(r"\n",gaps=True),
				      encoding="utf-8")
    # sents são listas de tokens em unicode
    sents=list(corpus.sents())
    
    output=anota_sentencas(sents,modelo,arquitetura)
    #print output[0][0]
    tagged_words=len(corpus.tagged_words())
    tagged_sents=list(corpus.tagged_sents())
    # transformação do padrão-ouro de unicode para string para
    # etiquetagem pelo AeliusRUBT.pkl e AeliusBRUBT.pkl
    # tagged_sents=AnotaCorpus.codifica_sentencas_anotadas(tagged_sents)
    #if arquitetura == "nltk":
    #    tagged_sents=codifica_sentencas_anotadas(tagged_sents)
    avalia(output,tagged_sents,tagged_words)

TestaEtiquetador=testa_etiquetador # compatibilidade com versões antigas

def imprime(lista_de_sentencas,arquivo):
    f=open(arquivo,"w")
    for m in range(len(lista_de_sentencas)):
        for n in  range(len(lista_de_sentencas[m])):
            p=lista_de_sentencas[m][n]
            palavra=p[0].encode("utf-8")
            etiqueta=p[1].encode("utf-8")
            f.write( "%s/%s " % (palavra,etiqueta) )
        f.write("\n")
    f.close()
            
def tempo(modelo,arquitetura="nltk",raiz=".",ouro="luzia_gold\.cap\d+\.txt"):
	t1=time.time()
	avalia.testa_etiquetador(modelo,arquitetura,raiz,ouro)
	t2=time.time()
	print "Tempo de avaliação do etiquetador %s: %f" % (modelo,(t2-t1))
	t1=time.time()
	avalia.testa_etiquetador(modelo,arquitetura,raiz,ouro)
	t2=time.time()
	print "Tempo de avaliação do etiquetador %s: %f" % (modelo,(t2-t1))

