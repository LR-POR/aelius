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
# $Id: AnotaTextosLXTagger.py $

import os
from Aelius.Extras import carrega
from Aelius.AnotaCorpus import anota_texto
from Aelius.Toqueniza import TOK_PORT_LX2

def CriaListadeArquivos(diretorio=".",prefixo=None,sufixo=None, infixo=None):
    if prefixo:
        return [a for a in os.listdir(diretorio) if a.startswith(prefixo)]
    else:
        if sufixo:
            return [a for a in os.listdir(diretorio) if a.endswith(sufixo)]
        else:
            if infixo:
                return [a for a in os.listdir(diretorio) if infixo in a]
            else:
                return os.listdir(diretorio)

def AnotaTextos(lista):
	for a in lista:
		anota_texto(a,lx,"mxpost",raiz=".",toquenizador=TOK_PORT_LX2, separacao_contracoes=True)

