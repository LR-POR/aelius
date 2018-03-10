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
# $Id: CorrigeTexto.py $

# O código seguinte constitui mera adapatação para o português do Brasil
# de classe de Python apresentada na seguinte obra:
# The following code is just an adaptation to Brazilian Portuguese of a
# Python class presented in the following book:

# PERKINS, Jacob. Python Text Processing with NLTK 2.0 Cookbook. Birmingham, UK: Packt, 2010. 256 p.

# A única diferença em relação à classe original é a atribuição
# do valor default 'pt_br' ao parâmetro  dict_name.
# The only difference to the original class is the attribution
# of the default value 'pt_br' to the dict_name parameter.

"""
>>> from Aelius import CorrigeTexto
>>> c=CorrigeTexto.SpellingReplacer()
>>> c.replace("caza")
'casa'
>>> c.replace("viagei")
'viajei'
>>> c.replace("viagem")
'viagem'
>>> c.replace("viajem")
'viajem'
>>> c.replace("antikakfianas")
'antikakfianas'
>>> 
"""
import enchant 
from nltk.metrics import edit_distance
class SpellingReplacer(object):
    def __init__(self, dict_name='pt_br', max_dist=2):
        self.spell_dict = enchant.Dict(dict_name)
        self.max_dist = 2

    def replace(self, word):
        if self.spell_dict.check(word):
            return word
        suggestions = self.spell_dict.suggest(word)
        if suggestions and edit_distance(word, suggestions[0]) <= self.max_dist:
            return suggestions[0]
        else:
            return word

correcao="<choice><sic>%s</sic><corr>%s</corr></choice>"
corretor=SpellingReplacer()
def anota_xml(palavra):
    output=corretor.replace(palavra)
    if output == palavra:
        return palavra
    else:
        return correcao % (palavra,output)
