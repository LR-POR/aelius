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
# $Id: ProcessaNomesProprios.py $

"""
Este módulo possibilita um tratamento mais adequado para a etiquetagem de nomes próprios.
Normalmente, os etiquetadores tendem a tratar como nome próprio toda palavra com inicial maiúscula.
Por exemplo, a sentença 'Cidade grande tem mais problemas.' foi anotada da seguinte forma pelo LX-Tagger,
em teste realizado on-line em 3 de abril de 2012:

<p><s> Cidade/PNM grande/GRANDE/ADJ#gs tem/TER/V#pi-3s mais/ADV problemas/PROBLEMA/CN#mp ./PNT </s></p> 

Fonte: http://lxcenter.di.fc.ul.pt/services/pt/LXServicesSuitePT.html

Nesse exemplo, o token 'Cidade', por estar maisculizado no início de sentença, é erroneamente tratado
como nome próprio (etiqueta PNM) em vez de nome comum (etiqueta CN).
O presente módulo oferece a função minusculiza_nao_nomes_proprios(lista_de_sentencas),
que minusculiza toda palavra inicial das sentenças de um texto, 
exceto aquelas que ocorrem com inicial maiúscula em posição não inicial. Ver exemplo abaixo. 
As sentenças assim processadas é que devem ser dadas como entrada ao etiquetador. 
Após a etiquetagem, essas sentenças são restituídas à forma original, com toda palavra inicial 
maisculizada, por meio da função maiusculiza_inicio_de_sentenca(sentenca). Para uma demostração
do funcionamento dessas funções, execute a função main().
"""
import string, nltk

TEXTO = """– Luzia pediu a Deus e a Ávila para que lhe ajudassem a sair de Sobral .
Deus ajudou Luzia .
... Sobral era uma cidade intelectual .
... Cidade intelectual , Sobral tinha muitos poetas .
Município intelectual , Sobral tinha muitos poetas .
Fortaleza era uma cidade provinciana .
Ávila ajudou Luzia .
... Cansada , Luzia logo dormiu .
Ávida por sossego , Luzia deixou a cidade .
Ótimo !
Bom .
... – Bom .
?
! ? ? –""".decode("utf-8")

SENTENCAS = TEXTO.splitlines()
SENTENCAS.append("")

# Na sentença "Fortaleza era uma cidade provinciana .",
# da lista cima, "Fortaleza" também será minusculizada, 
# embora seja nome próprio, porque só aparece em posição 
# inicial.



# Sinais de pontuação que podem
# ocorrer no início das sentenças;
# pressupõe-se que no texto ocorre apenas
# Unicode 2013 EN DASH e reticências como sinais
# de pontuação além dos definidos em string.punctuation:
PONTUACAO = "–".decode("utf-8")+ "..." + string.punctuation



# Palavras com inicial maiúscula em 
# posição não inicial:
DICIONARIO = nltk.defaultdict(int)

def extrai_palavra_inicial(sentenca):
	'''Extrai índice da palavra que se encontra no início de uma sentença
dada, sob a forma de uma lista de tokens em unicode, com cada sinal de pontuação, tal como
definido na variável global PONTUACAO, representando um token. 
Caso iniciada por sinal de pontuação, esse é ignorado.
'''
	comprimento=len(sentenca)
	if comprimento < 1:
		return -1
	

	else:
		inicio=0
		indice=0
		condicao=True
		
		while condicao and comprimento > indice:
			# print sentenca
			# print len(sentenca), indice 
			if sentenca[indice] in PONTUACAO: # pressupõe entrada toquenizada
				inicio+=1
			else:
				condicao=False
				return inicio
			indice+=1
	return -1

def armazena_palavras_maiusculas(sentenca):
	inicio=extrai_palavra_inicial(sentenca)
	if inicio >= 0:		
		for palavra in sentenca[inicio+1:]:
			p=palavra
			if len(p) > 0 and p[0].isupper(): #aqui 14092010
				DICIONARIO[palavra]+=1
	#f=open("DICIONARIO_maiusculas.pkl","wb") # isso é mesmo necessário? 11042011: não!
	#dump(DICIONARIO,f,-1)
	#f.close()
            
def minusculiza_nao_nomes_proprios(lista_de_sentencas):
	for sent in lista_de_sentencas:
		if len(sent) > 0:
			armazena_palavras_maiusculas(sent)
	for sent in lista_de_sentencas:
		if len(sent) > 0:
			inicio=extrai_palavra_inicial(sent)
			if inicio >=0 and DICIONARIO[sent[inicio]] == 0:
            # print "Início da sentença:%s" % sent[inicio]
				palavra=sent[inicio]
				palavra=palavra.lower()
				sent[inicio]=  palavra
				
	# print DICIONARIO
	return lista_de_sentencas
            
def maiusculiza_inicio_de_sentenca(sentenca):
	inicio=extrai_palavra_inicial(sentenca)
	if inicio >= 0:
		palavra=sentenca[inicio]
		# print palavra
		#palavra=palavra.decode("utf-8")
		palavra="%s%s" % (palavra[0].upper(),palavra[1:])
		#sentenca[inicio]=palavra.encode("utf-8")
		sentenca[inicio]=palavra
		# print "Início da sentença:%s" % sentenca[inicio]
	return sentenca # como o argumento da função é uma lista, esta é
# alterada pela função, tornando-se desnecessário retorná-la; talvez fosse 
# mais elegante criar uma nova lista 

def separa_palavras_de_etiquetas(lista_de_tuplas):
	#print lista_de_tuplas # teste
	lista_de_palavras=[w for w,t in lista_de_tuplas]
	lista_de_etiquetas=[t for w,t in lista_de_tuplas]
	return lista_de_palavras,lista_de_etiquetas

def pprint(lista_de_sentencas):
	for sent in lista_de_sentencas:
		for p in sent:
			print p,
		print

def main():
    lista_de_sentencas=[]
    for sent in SENTENCAS:
	    lista_de_sentencas.append(sent.split())
    #for sent in lista_de_sentencas:
    #    armazena_palavras_maiusculas(sent)
    #print DICIONARIO
    lista_de_sentencas=minusculiza_nao_nomes_proprios(lista_de_sentencas)
    print "\nResultado da minusculização das palavras em início de sentença:\n"
    pprint(lista_de_sentencas)
    print "\nResultado da remaiusculização das palavras em início de sentença:\n"
    for i in range(len(lista_de_sentencas)):
	    lista_de_sentencas[i]=maiusculiza_inicio_de_sentenca(lista_de_sentencas[i])
    pprint(lista_de_sentencas)
 
if __name__ == '__main__':
    main()
