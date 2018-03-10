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
# $Id: Chunking.py $

"""Chunker simples de expressões nominais para o português baseado no tagset do LX-Tagger
http://lxcenter.di.fc.ul.pt/tools/pt/conteudo/LXTagger.html"""

import nltk
from os.path import join,splitext,expanduser

RAIZ=expanduser("~/analises")
TEXTO="actg.mxpost.txt"

CHUNKER= nltk.chunk.RegexpParser(r'''
NP:
{<DA>?<PNM>(<PREP>?<PNT>?<DA>?<CJ>?<PNM>)*}
{<QNT>?<DA>?<UM>?<IA>?<ORD>?<POSS>?<CARD>?<DEM>?<DGTR?>?<STT>*<AD[VJ]>*<PPA>*(<CN>|<WD>|<MHT>)<AD[VJ]>*<PPA>*}
''')

def CriaChunkedCorpus(raiz,texto,chunker=CHUNKER,destino=None,formato="trees"):
    """A partir de um arquivo na pasta 'raiz', anotado pelo LX-Tagger por meio da função AnotaCorpus.anota_texto() do Aelius, 
cria arquivo com chunks com base no chunker dado, no formato 'trees' ou 'IOB'.

>>> from Aelius import Extras, Toqueniza, AnotaCorpus, Chunking
>>> import os
>>> raiz,nome=os.path.split(Extras.carrega("actg.txt"))
>>> lx=Extras.carrega("lxtagger")
>>> os.chdir("../analises")
>>> AnotaCorpus.anota_texto(nome,lx,"mxpost",toquenizador=Toqueniza.TOK_PORT_LX2,raiz=raiz,separacao_contracoes=True)
Arquivo anotado:
actg.mxpost.txt
>>> Chunking.CriaChunkedCorpus(".","actg.mxpost.txt")
>>> s=open("actg.mxpost.trees.txt","rU").read().strip().split("\n\n")
>>> s[0]
'(S\n  (NP\n    Abordagens/PNM\n    Computacionais/PNM\n    de/PREP\n    a/DA\n    Teoria/PNM\n    de/PREP\n    a/DA\n    Gram\xc3\xa1tica/PNM)\n  ./PNT)'
>>> print s[0]
(S
  (NP
    Abordagens/PNM
    Computacionais/PNM
    de/PREP
    a/DA
    Teoria/PNM
    de/PREP
    a/DA
    Gramática/PNM)
  ./PNT)
>>> print s[5]
(S
  Em/PREP
  (NP a/DA Europa/PNM)
  e/CJ
  em/PREP
  (NP os/DA Estados/PNM Unidos/PNM)
  ,/PNT
  (NP a/DA área/CN)
  de/PREP
  (NP a/DA Linguística/PNM Computacional/PNM)
  está/V
  em/PREP
  (NP extrema/ADJ expansão/CN)
  e/CJ
  (NP goza/CN)
  de/PREP
  (NP muita/QNT popularidade/CN)
  ,/PNT
  tanto/ADV
  em/PREP
  (NP os/DA cursos/CN)
  de/PREP
  (NP Ciências/PNM)
  de/PREP
  (NP a/DA Computação/CN)
  quanto/REL
  nos/CL
  de/PREP
  (NP Linguística/PNM)
  ./PNT)
>>> from nltk import Tree
>>> Tree.parse(s[5])
Tree('S', ['Em/PREP', Tree('NP', ['a/DA', 'Europa/PNM']), 'e/CJ', 'em/PREP', Tree('NP', ['os/DA', 'Estados/PNM', 'Unidos/PNM']), ',/PNT', Tree('NP', ['a/DA', '\xc3\xa1rea/CN']), 'de/PREP', Tree('NP', ['a/DA', 'Lingu\xc3\xadstica/PNM', 'Computacional/PNM']), 'est\xc3\xa1/V', 'em/PREP', Tree('NP', ['extrema/ADJ', 'expans\xc3\xa3o/CN']), 'e/CJ', Tree('NP', ['goza/CN']), 'de/PREP', Tree('NP', ['muita/QNT', 'popularidade/CN']), ',/PNT', 'tanto/ADV', 'em/PREP', Tree('NP', ['os/DA', 'cursos/CN']), 'de/PREP', Tree('NP', ['Ci\xc3\xaancias/PNM']), 'de/PREP', Tree('NP', ['a/DA', 'Computa\xc3\xa7\xc3\xa3o/CN']), 'quanto/REL', 'nos/CL', 'de/PREP', Tree('NP', ['Lingu\xc3\xadstica/PNM']), './PNT'])
>>> print Tree.parse(s[5]).pprint()
(S
  Em/PREP
  (NP a/DA Europa/PNM)
  e/CJ
  em/PREP
  (NP os/DA Estados/PNM Unidos/PNM)
  ,/PNT
  (NP a/DA área/CN)
  de/PREP
  (NP a/DA Linguística/PNM Computacional/PNM)
  está/V
  em/PREP
  (NP extrema/ADJ expansão/CN)
  e/CJ
  (NP goza/CN)
  de/PREP
  (NP muita/QNT popularidade/CN)
  ,/PNT
  tanto/ADV
  em/PREP
  (NP os/DA cursos/CN)
  de/PREP
  (NP Ciências/PNM)
  de/PREP
  (NP a/DA Computação/CN)
  quanto/REL
  nos/CL
  de/PREP
  (NP Linguística/PNM)
  ./PNT)
>>> 
"""
    nome_do_destino=""
    if destino:
        nome_do_destino=destino
    else:
        nome_do_destino=join(raiz,"%s.%s.txt" % (splitext(texto)[0],formato))
    f=open(nome_do_destino,"w")
    c=nltk.corpus.TaggedCorpusReader(raiz,texto,encoding="utf-8")
    sents=c.tagged_sents()
    chunked_sents=chunker.batch_parse(sents)
    if formato=="IOB":
        for s in chunked_sents:
            s=nltk.chunk.tree2conllstr(chunker.parse(s))
            f.write("%s\n\n" % (s.encode("utf-8")))
    else:
        for s in chunked_sents:
            f.write("%s\n\n" % (s.pprint().encode("utf-8")))
    f.close()

def IOB2trees(arquivo):
    """A partir de um arquivo de sentenças cujos chunks do tipo NP estão anotados no formato IOB, retorna uma lista de árvores do tipo nltk.Tree.
    """
    linhas=open(arquivo).read().strip().split("\n\n")
    return [nltk.chunk.conllstr2tree(c) for c in linhas]

def avalia(arquivo,chunker=CHUNKER):
    """Avalia um chunker com base num arquivo no formato IOB corrigido por humano.
    """
    trees=IOB2trees(arquivo)
    print chunker.evaluate(trees)
    
def main():
    """Esta função pressupõe que o texto "actg.mxpost.txt', versão anotada pelo LX-Tagger, via Aelius, do texto 'actg.txt',
distribuído na pasta aelius_data, se encontra na pasta '~/analises'.
"""
    CriaChunkedCorpus(RAIZ,TEXTO,CHUNKER,destino=None,formato="trees")
    CriaChunkedCorpus(RAIZ,TEXTO,CHUNKER,destino=None,formato="IOB")
