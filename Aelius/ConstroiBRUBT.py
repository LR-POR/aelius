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
# $Id: ConstroiBRUBT.py $

from cPickle import dump
from nltk.tag import brill
from nltk.corpus import TaggedCorpusReader
from Extras import carrega
from AnotaCorpus import abre_etiquetador
from ConstroiRUBT import EXEMPLO,SENTENCA

TEMPLATES = [
    brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,1)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (2,2)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,2)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateTagsRule, (1,3)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,1)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (2,2)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,2)),
    brill.SymmetricProximateTokensTemplate(brill.ProximateWordsRule, (1,3)),
    brill.ProximateTokensTemplate(brill.ProximateTagsRule, (-1, -1), (1,1)),
    brill.ProximateTokensTemplate(brill.ProximateWordsRule, (-1, -1), (1,1))
]

INICIAL=carrega("AeliusRUBT.pkl")

def treina(expressao_regular,
               etiquetador=INICIAL,
               destino="BRUBT.pkl",
              raiz=".",
              codificacao="utf-8",
           max_rules=100, 
           min_score=3):
    inicial=abre_etiquetador(etiquetador)
    corpus=TaggedCorpusReader(raiz,
                         expressao_regular,
                         encoding=codificacao)
    train_sents=corpus.tagged_sents()
    trainer = brill.FastBrillTaggerTrainer(inicial,TEMPLATES)
    brubt = trainer.train(train_sents, max_rules= max_rules, min_score=min_score)
    print 'Etiquetagem da sentença-exemplo "%s"\n' % EXEMPLO,brubt.tag(SENTENCA)
    f=open(destino,"wb")
    dump(brubt,f, -1)
    f.close()
