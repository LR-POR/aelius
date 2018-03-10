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
# $Id: Toqueniza.py $

"""Este módulo oferece diversos recursos para a toquenizaçao de cadeias
em unicode, representando sentenças de línguas como a portuguesa.
Por toquenização de uma cadeia entende-se a transformação da cadeia
em uma lista de cadeias representando palavras, expressões numéricas
etc. da língua. 
O módulo permite toquenizar em diferentes estilos. Exemplo:

>>> from Aelius import Toqueniza
>>> print Toqueniza.TEXTO
O Dr. José P. Fernandes disse-lhe que a pistola .45 custa R$ 3,5 mil, 35.08% de Cz$ 3.800,98, às 18h30min da segunda-feira (22/10/2010). 
No passado. 
Dir-se-ia que ele deu com os burros n'água...
>>> for sent in Toqueniza.SENTENCAS:
	for t in Toqueniza.TOK_PORT.tokenize(sent):
		print t

		
O
Dr.
José
P.
Fernandes
disse
-
lhe
que
a
pistola
.45
custa
R$
3,5
mil
,
35.08
%
de
Cz$
3.800,98
,
às
18h30min
da
segunda
-
feira
(
22
/
10
/
2010
)
.
No
passado
.
Dir
-
se
-
ia
que
ele
deu
com
os
burros
n
'
água
...

No exemplo acima, hifens e apóstrofos são tratados como tokens independentes.
Para não separar esses elementos, deve-se utilizar o toquenizador Toqueniza.TOK_PORT_LX ou TOK_PORT_LX2,
que prepara uma sentença para ser anotada por meio da função 
Aelius.AnotaCorpus.anota_sentencas, quando o etiquetador
especificado como parâmetro for como o LXTagger. Consultar documentação de 
Aelius.AnotaCorpus.anota_sentencas.

>>> for sent in Toqueniza.SENTENCAS:
	for t in Toqueniza.TOK_PORT_LX.tokenize(sent):
		print t

		
O
Dr.
José
P.
Fernandes
disse-lhe
que
a
pistola
.45
custa
R$
3,5
mil
,
35.08
%
de
Cz$
3.800,98
,
às
18h30min
da
segunda-feira
(
22
/
10
/
2010
)
.
No
passado
.
Dir-se-ia
que
ele
deu
com
os
burros
n'água
...
>>> Toqueniza.TOK_PORT_LX2.tokenize('Esquecemo-nos de dizer-lhe que ela queria vendê-la.'.decode('utf-8'))
[u'Esquecemos', u'-nos', u'de', u'dizer', u'-lhe', u'que', u'ela', u'queria', u'vender', u'-la', u'.']

"""

import string, re, nltk

PALAVRAS_COM_CLITICO="quebra-cabeça esquecemo-nos vimo-la vendê-lo parti-la partí-lo levaram levaram-no levá-las levar-lhes queixar-se esqueci-me lembrei-te elogiou-o elogiaram-nas levou-as levá-lo comprá-lo queixou-se".decode("utf-8").split()

# Para facilitar a testagem do módulo, definimos a variável global SENT:
SENT="""O Prof. Leonel (UFC) chamou a atenção para o fato de que a toquenização é um processo não trivial,
devido, sobretudo, às abreviaturas."""
# Decodificação da cadeia unicode utilizando a codificação utf-8:
SENT=SENT.decode("utf-8")

# Outros exemplos para testar toquenização:
TEXTO="""O Dr. José P. Fernandes disse-lhe que a pistola .45 custa R$ 3,5 mil, 35.08% de Cz$ 3.800,98, às 18h30min da segunda-feira (22/10/2010). 
No passado. 
Dir-se-ia que ele deu com os burros n'água...""".decode("utf-8")
SENTENCAS=TEXTO.split("\n")

SINAIS=string.punctuation

# Esta lista contém apenas algumas das abreviaturas mais comuns,
# não sendo, portanto, exaustiva. Deve ser complementada consultando-se
# dicionários e pesquisando-se em corpora.
ABREVIATURAS="Prof Profa Sr Sra Dr Dra".split()


# Hífen, apóstrofo e ponto como parte de palavra;
# esta expressão deve ser usada para toquenizar textos
# a serem anotados por etiquetadores como o LX-Tagger;
# o ponto final delimitador de sentença, contudo, não é separado:
EX='''(?x)[A-Za-z]+[.$]| # palavras terminando em ponto ou cifrão
[)(!?"]| # sinais de pontuação
\.\d+| # expressões numéricas como .45
\d+[.,]\d+[.,]\d+| # números como 3.800,98
\d+[.,]\d+| # números como 3,5 e 3.5
\w+([-\']\w+|\w+)* | # palavras com ou sem hífen ou apóstrofo
\.{2,} | # dois ou mais pontos (reticências)
[^\w\s]+ # não palavras e não espaços'''

# Toqueniza sem separar hifens, apóstrofos e pontos,
# conforme descrição acima.
_TOK_PORT_LX=nltk.RegexpTokenizer(EX)

def SeparaPontoFinal(s):
	"""Toqueniza reticências e pontos finais delimitadores 
	de sentenças, mas não pontos que constituem parte de palavras.
	"""
	s=s.rstrip()
	if s.endswith("..."):
		return "%s ..." % s[:-3] # insere espaço antes deste delimitador de sentença
	elif s.endswith("."):
		return "%s ." % s[:-1]  # insere espaço antes deste delimitador de sentença
	else:
		return s

class ToquenizadorBifasico():
	"""Esta classe oferece método tokenize que toqueniza em duas 
	fases. Por exemplo:

>>> from Aelius.Toqueniza import TOK_PORT_LX
>>> from Aelius.Toqueniza import SENTENCAS
>>> for s in SENTENCAS:
	for t in TOK_PORT_LX.tokenize(s):
		print t
	print

	
O
Dr.
José
P.
Fernandes
disse-lhe
que
a
pistola
.45
custa
R$
3,5
mil
,
35.08
%
de
Cz$
3.800,98
,
às
18h30min
da
segunda-feira
(
22
/
10
/
2010
)
.

No
passado
.

Dir-se-ia
que
ele
deu
com
os
burros
n'água
...

>>> 
	Nesse exemplo, primeiro, os pontos são tratados como parte de palavras.
	Depois, separam-se os pontos finais delimitadores de sentenças.
	Uma instância desta classe pode ser atribuída ao argumento-chave
	word_tokenizer de leitores de corpus do NLTK, como o 
	nltk.corpus.PlaintextCorpusReader.
	"""

	def __init__(self, Tokenizer_Function,NLTK_Tokenizer):
		self._tokenizer1 = Tokenizer_Function
		self._tokenizer2 = NLTK_Tokenizer

	def tokenize(self,sent):
		return self._tokenizer2.tokenize(self._tokenizer1(sent))

# Toquenizador para o LX-Tagger
TOK_PORT_LX=ToquenizadorBifasico(SeparaPontoFinal,_TOK_PORT_LX)

def ExtraiToquenizadorPUNKT():
	"""Verifica se o toquenizador PUNKT está instalado. Em caso negativo, descarrega-o da Internet. Retorna esse toquenizador.
	"""
	try:
		nltk.data.find('tokenizers/punkt/portuguese.pickle')
	except:
		nltk.download("punkt")
		
	finally:
		return nltk.data.load('tokenizers/punkt/portuguese.pickle')
	
# Toquenizador sentencial próprio para textos em formato "bruto",
# em que há quebras de linha dentro das sentenças:
PUNKT= ExtraiToquenizadorPUNKT()


# Toquenizador sentencial para textos pré-processados
# em que cada sentença está numa linha própria:
# REGEXP=nltk.RegexpTokenizer(r"\n",gaps=True)

# Expressão regular que define a noção default de token vocabular
# em português do Aelius, segundo a qual hífen e apóstrofos
# constituem tokens separados:
EXP_REG_AELIUS='''(?x)[A-Za-z]+[.$]| # palavras terminando em ponto ou cifrão
[)(!?"]| # sinais de pontuação
\.\d+| # expressões numéricas como .45
\d+[.,]\d+[.,]\d+| # números como 3.800,98
\d+[.,]\d+| # números como 3,5 e 3.5
\w+| # tokens alfanuméricos
\.{2,} | # dois ou mais pontos (reticências)
[^\w\s]+ # não palavras e não espaços'''

# Toquenizador default, separa hifens e apóstrofos
TOK_ER = nltk.RegexpTokenizer(EXP_REG_AELIUS)
# Toquenizador para textos a serem anotados no estilo
# default do Aelius
TOK_PORT=ToquenizadorBifasico(SeparaPontoFinal,TOK_ER)

# outras funções de toquenização
# funções auxiliares
def toquenizaSentenca(sentenca):
	"""Esta função transforma unicode em uma lista de tokens unicode."""
	t="" # inicializamos uma cadeia vazia
	for c in sentenca:
		# a cada volta do laço, t é atualizada
		if c in SINAIS: # se c é sinal de pontuação, um espaço é inserido de ambos os lados, o resultado sendo concatenado a t
			t="%s %s " % (t,c) 
		else: # se c não é sinal de pontuação, c é simplesmente concatenado a t
			t="%s%s" % (t,c)
	return t.split()

def processaAbreviaturas(tokens):
	"""Esta função corrige, em uma lista de tokens, os casos em que o ponto foi indevidamente separado das abreviaturas listadas na variável global ABREVIATURAS."""
	i=0
	while i < len(tokens)-1:
		for a in ABREVIATURAS:
# minusculizamos antes de realizar a comparação entre as duas instâncias de unicode, de modo a dar conta de variaçãoes na grafia como "Dr." e "dr."
			if tokens[i].lower() ==a.lower()  and tokens[i+1] == ".":
				# transformamos casos como "Prof" em "Prof."
				tokens[i]="%s." % tokens[i]
				# excluímos o ponto
				tokens.pop(i+1)
		i+=1

# função de toquenização propriamente dita
def toquenizaPontuacao(sentenca=SENT):
    """A partir de cadeia dada, retorna outra cadeia em que os sinais de
    pontuação da variável global SINAIS estão separados das palavras,
    exceto no caso dos itens listados na variável global ABREVIATURAS.

>>> for t in Toqueniza.toquenizaPontuacao():
	print t

	
O
Prof.
Leonel
(
UFC
)
chamou
a
atenção
para
o
fato
de
que
a
toquenização
é
um
processo
não
trivial
,
devido
,
sobretudo
,
às
abreviaturas
.
>>> 
"""
    tokens=toquenizaSentenca(sentenca)
    processaAbreviaturas(tokens)
    return tokens

def exibeTokens(tokens):
    """
    Apresenta sentença toquenizada no formato canônico, como string.
    """
    tokens=[t.encode("utf-8") for t in tokens]
    return " ".join(tokens)


def SeparaClitico(palavra):
	"""Separa pronomes em ênclise, restaurando a forma canônica das formas verbais que sofrem alomorfias quando da adjunção de clíticos.
>>> for p in Toqueniza.PALAVRAS_COM_CLITICO:
	print Toqueniza.SeparaClitico(p)

	
quebra-cabeça
esquecemos nos
vimos la
vender lo
partir la
partir lo
levaram
levaram no
levar las
levar lhes
queixar se
esqueci me
lembrei te
elogiou o
elogiaram nas
levou as
levar lo
comprar lo
queixou se
	"""
	cliticos=r"me|te|os?|as?|los?|las?|nos?|nas?|nos|vos|lhes?|se"
	if "-" in palavra:
		partes=palavra.split("-")
		m=re.match(cliticos,partes[-1])
		if m:
			clitico=m.group()
			if clitico.startswith("lo") or clitico.startswith("la") or clitico.startswith("nos"):
				if partes[0].endswith("mo".decode("utf-8")):
					partes[0]="%smos" % partes[0][:-2]
				elif partes[0].endswith("á".decode("utf-8")):
					partes[0]="%sar" % partes[0][:-1]
				elif partes[0].endswith("ê".decode("utf-8")):
					partes[0]="%ser" % partes[0][:-1]
				elif partes[0].endswith("í".decode("utf-8")):
					partes[0]="%sir" % partes[0][:-1]
				else:
					partes[0]="%sr" % partes[0]
			return " ".join(partes)



	return palavra

def ToquenizaCliticos(lista_de_tokens):
	tokens=[]
	for w in lista_de_tokens:
		tokens.extend(SeparaClitico(w).split(" "))
	return tokens

def ToquenizaCliticosLX(lista_de_tokens):
	tokens=[]
	for w in lista_de_tokens:
		tokens.extend(SeparaCliticoLX(w).split(" "))
	return tokens

class ToquenizadorMM():
	"""
	Toqueniza uma sentença no estilo do corpus Mac-Morpho ou conforme o exigido pelo LX-Tagger.
	Opera em três etapas, necessitando de três argumentos para ser inicializado: 
	(i) uma função que separa os pontos finais;
	(ii) um toquenizador do NLTK que identifica tokens por meio de expressões regulares;
	(iii) uma função que separa os clíticos e normaliza as formas verbais.
	

	"""
	def __init__(self, Tokenizer_Function1,NLTK_Tokenizer,Tokenizer_Function2):
		self._tokenizer1 = Tokenizer_Function1
		self._tokenizer2 = NLTK_Tokenizer
		self._tokenizer3 = Tokenizer_Function2
	def tokenize(self,sent):
		return self._tokenizer3(self._tokenizer2.tokenize(self._tokenizer1(sent)))

TOK_PORT_MM=ToquenizadorMM(SeparaPontoFinal,_TOK_PORT_LX,ToquenizaCliticos)
def SeparaCliticoLX(palavra):
	"""Acrescenta um hífen antes dos clíticos em ênclise, como exigido pelo LX-Tagger. No entanto, diferentemente da toquenização original desse etiquetador, esta função retorna as formas canônicas do infinitivo, como 'vender' e 'comprar' em vez de 'vendê#' e 'comprá#'. Por outro lado, formas de primeira pessoa do plural com pronomes enclíticos do tipo de 'esquecemo-nos' e 'esquecemo-la' são toquenizadas como 'esquecemos -nos' e 'esquecemos -la' em vez de 'esquecemo -nos' e 'esquecemo -la', como no LX-Tagger, o que dificulta a lematização. A toquenização de formas com mesóclise do tipo de 'comprar-se-ia', cada vez mais raras no português do Brasil, ainda não foi implementada.
	
>>> from Aelius import Toqueniza
>>> for palavra in Toqueniza.PALAVRAS_COM_CLITICO:
	print Toqueniza.SeparaCliticoLX(palavra)

	
quebra-cabeça
esquecemos -nos
vimos -la
vender -lo
partir -la
partir -lo
levaram
levaram -no
levar -las
levar -lhes
queixar -se
esqueci -me
lembrei -te
elogiou -o
elogiaram -nas
levou -as
levar -lo
comprar -lo
queixou -se

	"""
	lista=SeparaClitico(palavra).split()
	if len(lista) ==2:
		return "%s -%s" % (lista[0],lista[1])
	else:
		return palavra

TOK_PORT_LX2=ToquenizadorMM(SeparaPontoFinal,_TOK_PORT_LX,ToquenizaCliticosLX)
