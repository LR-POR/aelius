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
# $Id: ExpandeContracoes.py $

		
def expande(s):
	"""Esta função toma contração em unicode como entrada e a expande, retornando uma dupla.
"""
	if s.lower().startswith("d"):
		return ("%se" % s[0],s[1:])
	elif s.lower().startswith("n"):
		return ("em",s[1:]) # talvez seja necessário converter em maiúscula em alguns casos
	elif s.lower() == ("à".decode("utf-8")):
		return ("a","a" )
	elif s.lower() == ("às".decode("utf-8")):
		return ("a","as" )
	elif s.lower() == ("ao"):
		return ("a","o" )
	elif s.lower() == ("aos"):
		return ("a","os" )
	elif s.lower().startswith("à".decode("utf-8")):
		return ("a","a%s" % s[1:])
	elif s.lower().startswith("pel"): # a preposição "pra", se anotada como "pra/P+D-F",
		# provoca quebra do programa
		return ("por","%s" % s[3:])
	elif s.lower() == ("comigo"):
		return ("com","mim" )
	elif s.lower() == ("contigo"):
		return ("com","ti" )
	elif s.lower() == ("consigo"):
		return ("com","si" )
	elif s.lower() == ("conosco"):
		return ("com","nós".decode("utf-8"))
	elif s.lower() == ("convosco"):
		return ("com","vós".decode("utf-8") )
	elif s.lower().startswith("-m") or s.lower().startswith("-t"):
		return ("%se" % s[:2],"%s" % s[2:] )
	elif s.lower().startswith("-lh"): # não leva em conta "lhes" + "o" etc.; forma expandida é sempre "lhe"
		return ("%se" % s[:3],"%s" % s[3:] )
	else:
		return s,"CL"

	
def expande_contracoes(sentenca):
	"""Toma uma sentença anotada, sob a forma de uma lista de duplas (palavra,etiqueta), conforme o sistema do Aelius (baseado no do Corpus Histórico do Português Tycho Brahe) e retorna uma versão em que os tokens cujas etiquetas contenham o símbolo '+' são expandidos pela função expande(). Por exemplo, o par ('na', 'P+D-F') desdobra-se nos dois pares ('em','P') e (u'a', u'D-F').
	
>>> from Aelius import ExpandeContracoes, AnotaCorpus
>>> tokens1=AnotaCorpus.TOK_PORT.tokenize(AnotaCorpus.EXEMPLO)
>>> anotados=AnotaCorpus.anota_sentencas([tokens1],AnotaCorpus.TAGGER)
>>> anotados
[[(u'Os', u'D-P'), (u'candidatos', u'N-P'), (u'classific\xe1veis', u'ADJ-G-P'), (u'dos', u'P+D-P'), (u'cursos', u'N-P'), (u'de', u'P'), (u'Sistemas', u'NPR-P'), (u'de', u'P'), (u'Informa\xe7\xe3o', u'NPR'), (u'poder\xe3o', u'VB-R'), (u'ocupar', u'VB'), (u'as', u'D-F-P'), (u'vagas', u'ADJ-F-P'), (u'remanescentes', u'ADJ-G-P'), (u'do', u'P+D'), (u'Curso', u'NPR'), (u'de', u'P'), (u'Engenharia', u'NPR'), (u'de', u'P'), (u'Software', u'NPR'), (u'.', u'.')]]
>>> ExpandeContracoes.expande_contracoes(anotados[0])
[(u'Os', u'D-P'), (u'candidatos', u'N-P'), (u'classific\xe1veis', u'ADJ-G-P'), (u'de', u'P'), (u'os', u'D-P'), (u'cursos', u'N-P'), (u'de', u'P'), (u'Sistemas', u'NPR-P'), (u'de', u'P'), (u'Informa\xe7\xe3o', u'NPR'), (u'poder\xe3o', u'VB-R'), (u'ocupar', u'VB'), (u'as', u'D-F-P'), (u'vagas', u'ADJ-F-P'), (u'remanescentes', u'ADJ-G-P'), (u'de', u'P'), (u'o', u'D'), (u'Curso', u'NPR'), (u'de', u'P'), (u'Engenharia', u'NPR'), (u'de', u'P'), (u'Software', u'NPR'), (u'.', u'.')]
>>> sent="Espantou-me cumprimentarem-se.".decode("utf-8")
>>> t=AnotaCorpus.TOK_PORT.tokenize(sent)
>>> t
[u'Espantou', u'-', u'me', u'cumprimentarem', u'-', u'se', u'.']
>>> anotados=AnotaCorpus.anota_sentencas([t],AnotaCorpus.TAGGER)
>>> anotados
[[(u'Espantou', u'VB-D'), (u'-', u'+'), (u'me', u'CL'), (u'cumprimentarem', u'VB-F'), (u'-', u'+'), (u'se', u'SE'), (u'.', u'.')]]
>>> ExpandeContracoes.expande_contracoes(anotados[0])
[(u'Espantou', u'VB-D'), (u'me', u'CL'), (u'cumprimentarem', u'VB-F'), (u'se', u'SE'), (u'.', u'.')]

	"""
	lista=[]
	for w,t in sentenca:
		# é preciso assegurar que a etiqueta não seja apenas "+", atribuída, no sistema do Aelius, ao hífen
		if len(t) > 2 and "+" in t:
			t1,t2=t.split("+")
			w1,w2=expande(w)
			lista.extend([(w1,t1),(w2,t2)])
		else:
			if not w=="-": # exclusão de hífen como token
				lista.append((w,t))
	return lista

# Falta integrar no módulo as funções abaixo, de modo a obter uma toquenização de formas com hífen,
# como as do exemplo seguinte, idêntica à do LX-Tagger:
# Espantou-me cumprimentarem-se, dir-te-ia.
# Anotação pele versão on-line do LX-Tagger:
# <p><s> Espantou/ESPANTAR/V#ppi-3s -me/CL#gs1 cumprimentarem/CUMPRIMENTAR/V#INF-3p -se/CL#gn3 ,*//PNT dir-CL-ia/DIZER/V#c-3s -te/CL#gs2 ./PNT </s></p> 
# Fonte: http://lxcenter.di.fc.ul.pt/services/pt/LXServicesSuitePT.html

def clitico(forma):
	"""Testa se uma etiqueta é um clítico (CL ou SE na anotação do CHPTB) ou uma combinação de clíticos.
	"""
	return forma=="CL" or forma=="SE" or forma.startswith("CL+") or forma.startswith("SE+")

# Falta dar um tratamento adequado às formas mesoclíticas
def ProcessaFormasHifenizadas(t):
	"""Toma como entrada uma sentença anotada conforme o modelo do Aelius, que separa as formas ligadas por hífen, e altera a sentença original concatenando o hífen a cada forma pronominal enclítica ou mesoclítica bem como juntando os elementos de compostos como 'terça-feira' e 'pé-de-meia'.

>>> from Aelius import AnotaCorpus, ExpandeContracoes
>>> sent="Espantou-me cumprimentarem-se, dir-te-ia terça-feira.".decode("utf-8")
>>> t=AnotaCorpus.TOK_PORT.tokenize(sent)
>>> anotados=AnotaCorpus.anota_sentencas([t],AnotaCorpus.TAGGER)
>>> anotados
[[(u'Espantou', u'VB-D'), (u'-', u'+'), (u'me', u'CL'), (u'cumprimentarem', u'VB-F'), (u'-', u'+'), (u'se', u'SE'), (u',', u','), (u'dir', u'VB'), (u'-', u'+'), (u'te', u'CL'), (u'-', u'+'), (u'ia', u'-R'), (u'ter\xe7a', u'NPR'), (u'-', u'+'), (u'feira', u'NPR'), (u'.', u'.')]]
>>> ExpandeContracoes.ProcessaFormasHifenizadas(anotados[0])
-me
-se
-te
>>> anotados[0]
[(u'Espantou', u'VB-D'), (u'-', u'+'), (u'-me', u'CL'), (u'cumprimentarem', u'VB-F'), (u'-', u'+'), (u'-se', u'SE'), (u',', u','), (u'dir', u'VB'), (u'-', u'+'), (u'-te', u'CL'), (u'-', u'+'), (u'ia', u'-R'), (u'ter\xe7a-feira', u'NPR'), (u'.', u'.')]

	"""
	i=1
	c=len(t)
	while(i<c):
		if clitico(t[i][1]) and t[i-1]==("-","+"):
			print "-%s" % t[i][0] # remover após integração da função no módulo
			t[i]=("-%s" % t[i][0],t[i][1])
		if t[i]==("-","+") and not clitico(t[i+1][1]) and not clitico(t[i-1][1]):
			#print "%s-%s" % (t[i-1][0], t[i+1][0])
			t[i]=("%s-%s" % (t[i-1][0], t[i+1][0]),t[i+1][1])
			del t[i+1]
			del t[i-1]
			i-=2
			c-=2
		i+=1
