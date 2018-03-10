#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Aelius Brazilian Portuguese POS-Tagger and Corpus Annotation Tool
#
# Interface to FreeLing open-source POS-tagger and Lemmatizer
#
# Copyright (C) 2010-2013 Leonel F. de Alencar
# Author: Leonel F. de Alencar <leonel.de.alencar@ufc.br>
# URL: <http://sourceforge.net/projects/aelius/>
# For license information, see LICENSE.TXT
#
# $Id: FreeLing.py $

# Code and documentation mostly adapted from the following open source,
# licensed under the Apache License, Version 2.0:
# Natural Language Toolkit: Interface to the HunPos POS-tagger
#
# Copyright (C) 2001-2011 NLTK Project
# Author: Peter Ljunglöf <peter.ljunglof@heatherleaf.se>
#         David Nemeskey <nemeskeyd@gmail.com> (modifications)
#         Attila Zseder <zseder@gmail.com> (modifications)
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT
#
# $Id: hunpos.py $

"""
A module for interfacing with FreeLing open-source POS-tagger and Lemmatizer.
"""

import os
from subprocess import Popen, PIPE
import nltk

_FreeLing_url = 'http://nlp.lsi.upc.edu/freeling/'

_FreeLing_charset = 'utf-8'
"""The default encoding used by FreeLing: utf-8."""

FREELING_OUTPUT="""O
o
DA0MS0
	morro
morro
NCMS000
	de
de
SPS00
	o
o
DA0MS0
	Curral_de_o_Açougue
curral_de_o_açougue
NP00000
	emergia
emergir
VMII3S0
	em
em
SPS00
	suave
suave
AQ0CS0
	declive
declive
NCMS000
	de
de
SPS00
	a
o
DA0FS0
	campina
campina
NCFS000
	ondulada
ondular
VMP00SF
	.
.
Fp""".decode("utf-8")

def ProcessaOutputFreeLing(linhas):
    """This function is for demo purposes only. It processes
a file with output from the online FreeLing PosTagger and returns a list
with tuples (word, tag, lemma). 
"""
    i=0
    resultado=[]
    c=len(linhas)
    while i < c:
        resultado.append((linhas[i].strip(),linhas[i+1].strip(),linhas[i+2].strip()))
        i+=3
    return resultado

class FreeLingTokenizer():
    def __init__(self):
        pass
    
    def tokenize(self,sentence):
        tuplas=tuplas=ProcessaOutputFreeLing(FREELING_OUTPUT.split("\n"))
        return [token for token,tag,lemma in tuplas]

class FreeLingTagger(nltk.TaggerI):
    """
    A class for pos tagging and lemmatizing with FreeLing. The input is the paths to:
     - a model trained on training data
     - (optionally) the path to FreeLing binary named FreeLing
     - (optionally) the encoding of the training data (default: utf-8)

    Example:
	>>> from Aelius.FreeLing import FreeLingTagger, FreeLingTokenizer
        >>> from Aelius.Extras import carrega
        >>> tok=FreeLingTokenizer()
        >>> model=carrega('AeliusFreeLing')
        >>> sent="O morro do Curral do Açougue emergia em suave declive da campina ondulada.".decode("utf-8")
        >>> tokens=tok.tokenize(sent)
        >>> tagger = FreeLingTagger(model)
        >>> tagger.tag(tokens)
        [('O', 'o', 'DA0MS0'), ('morro', 'morro', 'NCMS000'), ('de', 'de', 'SPS00'), ('o', 'o', 'DA0MS0'), ('Curral_de_o_A\xc3\xa7ougue', 'curral_de_o_a\xc3\xa7ougue', 'NP00000'), ('emergia', 'emergir', 'VMII3S0'), ('em', 'em', 'SPS00'), ('suave', 'suave', 'AQ0CS0'), ('declive', 'declive', 'NCMS000'), ('de', 'de', 'SPS00'), ('a', 'o', 'DA0FS0'), ('campina', 'campina', 'NCFS000'), ('ondulada', 'ondular', 'VMP00SF'), ('.', '.', 'Fp')]
        >>> tagger.close()

    This class communicates with the FreeLing binary via pipes. When the
    tagger object is no longer needed, the close() method should be called to
    free system resources. The class supports the context manager interface; if
    used in a with statement, the close() method is invoked automatically:

        >>> with FreeLingTagger(model) as tagger:
        ...     tagger.tag(tokens)
        ...
        [('O', 'o', 'DA0MS0'), ('morro', 'morro', 'NCMS000'), ('de', 'de', 'SPS00'), ('o', 'o', 'DA0MS0'), ('Curral_de_o_A\xc3\xa7ougue', 'curral_de_o_a\xc3\xa7ougue', 'NP00000'), ('emergia', 'emergir', 'VMII3S0'), ('em', 'em', 'SPS00'), ('suave', 'suave', 'AQ0CS0'), ('declive', 'declive', 'NCMS000'), ('de', 'de', 'SPS00'), ('a', 'o', 'DA0FS0'), ('campina', 'campina', 'NCFS000'), ('ondulada', 'ondular', 'VMP00SF'), ('.', '.', 'Fp')]
    """

    def __init__(self, path_to_model, path_to_bin=None,
                 encoding=_FreeLing_charset, verbose=False):
        """
        Starts the FreeLing-tag executable and establishes a connection with it.
        
        @param path_to_model: The model file.
        @param path_to_bin: The FreeLing-tag binary.
        @param encoding: The encoding used by the model. C{unicode} tokens
            passed to the tag() and batch_tag() methods are converted to
            this charset when they are sent to FreeLing-tag.
            The default is utf-8.

            This parameter is ignored for C{str} tokens, which are sent as-is.
            The caller must ensure that tokens are encoded in the right charset.
        """
        FreeLing_paths = ['.', '/usr/bin', '/usr/local/bin', '/opt/local/bin',
                        '/Applications/bin', '~/bin', '~/Applications/bin']
        FreeLing_paths = map(os.path.expanduser, FreeLing_paths)

        self._FreeLing_bin = nltk.internals.find_binary(
                'FreeLing', path_to_bin, 
                env_vars=('FREELING', 'FREELING_HOME'),
                searchpath=FreeLing_paths, 
                url=_FreeLing_url, 
                verbose=verbose)

        if not os.path.isfile(path_to_model):
            raise IOError("FreeLing model file not found: %s" % model_file)
        self._FreeLing_model = path_to_model
        self._encoding = encoding
        self._FreeLing = Popen([self._FreeLing_bin, self._FreeLing_model],
                             shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self._closed = False
        def __del__(self):
        	self.close()

    def close(self):
        """Closes the pipe to the FreeLing executable."""
        if not self._closed:
            self._FreeLing.communicate()
            self._closed = True

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def tag(self, tokens):
        """Tags and lemmatizes a single sentence: a list of words.
        The tokens should not contain any newline characters.
        """
       
        
                
        tagged_tokens=ProcessaOutputFreeLing(self._FreeLing.stdout.readlines())
        
        
        return tagged_tokens

