#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Aelius Brazilian Portuguese POS-Tagger and Corpus Annotation Tool
#
# Copyright (C) 2010-2012 Leonel F. de Alencar
# Author: Leonel F. de Alencar <leonel.de.alencar@ufc.br>
#          
# URL: <http://sourceforge.net/projects/aelius/>
# For license information, see LICENSE.TXT
#
# $Id: ConstroiRUBT.py $

import cPickle, time
from nltk.tag import UnigramTagger,BigramTagger,TrigramTagger
from nltk.corpus import TaggedCorpusReader
from AnotaCorpus import abre_etiquetador,codifica_sentencas
from Toqueniza import TOK_PORT

# Exemplo extraído de "Recordações do Escrivão Isaias Caminha",
# de Lima Barreto
EXEMPLO='''Se os senhores algum dia quiserem encontrar um representante da grande nação brasileira, não o procurem nunca na sua residência. '''

#SENTENCA=codifica_sentencas([TOK_PORT.tokenize(EXEMPLO)])[0]
SENTENCA=TOK_PORT.tokenize(EXEMPLO.decode("utf-8"))

PARAMETROS={}

# A seguinte função foi extraída da p. 90 do seguinte livro:
# PERKINS, J.Python (2010). Text Processing with NLTK 2.0 Cookbook. 
# Birmingham, UK: Packt.
def backoff_tagger(train_sents, tagger_classes, backoff=None):
	for cls in tagger_classes:
		backoff = cls(train_sents, backoff=backoff)
	
	return backoff


def treina(expressao_regular,
               etiquetador,
               destino,
              raiz=".",
              proporcoes=[100],
               razao=1.0,
               codificacao="utf-8"):
    regexp_tagger=abre_etiquetador(etiquetador)
    corpus=TaggedCorpusReader(raiz,
                         expressao_regular,
                         encoding=codificacao)
    print "Conjunto de treino:\n%s\n" % " \n".join(corpus.fileids())
    sents=corpus.tagged_sents()
    #print sents[3]
    #print type(sents[3][0][0])
    c=len(sents)
    # proporção do conjunto de desenvolvimento
    # em relação a um determinado corpus
    # proporcoes=[10,30,50,70,100] 
    # razão entre sentencas de treino e total de sentencas
    # razao=0.75

    for n in proporcoes:
        proporcao=n/100.0
        size=int(c*proporcao)
        dev=sents[:size]
        size=int(len(dev)*razao)
        train=dev[:size]
        print "\n\nQuantidade de sentenças"
        print "Conjunto de treinamento: %d" % len(train)
        print "Total de %d tokens" % len(sum(train, []))
        test=dev[size:]
        print "Conjunto de teste: %d sentenças" % len(test)
        print "Total de %d tokens" % len(sum(test, []))
        t1=time.time()
        rubt=backoff_tagger(train,
                                 [UnigramTagger,BigramTagger,TrigramTagger],
                                 backoff=regexp_tagger)
        t2=time.time()
        print "Tempo de treinamento em segundos: %f" % (t2-t1)
        print 'Etiquetagem da sentença-exemplo "%s"\n' % EXEMPLO,rubt.tag(SENTENCA)
        f=open(destino,"wb")
        cPickle.dump(rubt,f,-1)
        if razao < 1.0:
            t1=time.time()
	    # introduzir avaliação por meio de Avalia.testa_etiquetador
            print "\nAcurácia na etiquetagem do conjunto de teste: %f" % rubt.evaluate(test)
            t2=time.time()
            print "Tempo de avaliação em segundos: %f" % (t2-t1)
    

