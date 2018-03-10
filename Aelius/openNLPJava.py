#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Aelius Brazilian Portuguese POS-Tagger and Corpus Annotation Tool
#
# Interface to the Java command of the OpenNLP open-source POS-tagger
#
# Copyright (C) 2010-2013 Leonel F. de Alencar
# Author: Leonel F. de Alencar <leonel.de.alencar@ufc.br>
# URL: <http://sourceforge.net/projects/aelius/>
# For license information, see LICENSE.TXT
#
# $Id: openNLP.py $

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
# $Id: openNLP.py $

"""
A module for interfacing with the Java command of the OpenNLP open-source POS-tagger.
"""

import os
from subprocess import Popen, PIPE
import nltk

_openNLP_url = 'http://opennlp.apache.org/'

_openNLP_charset = 'utf-8'
"""The default encoding used by openNLP: utf-8."""

class openNLPTagger(nltk.TaggerI):
    """
    A class for pos tagging with openNLP. The input is the paths to:
     - a model trained on training data
     - (optionally) the path to the opennlp-tools jar file (opennlp-tools.jar). If not specified here, then this file must be specified in the CLASSPATH envinroment variable.
     - (optionally) the encoding of the training data (default: utf-8)

    Example:
		>>> from Aelius.openNLPJava import openNLPTagger
        >>> tagger = openNLPTaggerJava('en-pos-maxent.bin')
        >>> tagger.tag('What is the airspeed of an unladen swallow ?'.split())
        [('What', 'WP'), ('is', 'VBZ'), ('the', 'DT'), ('airspeed', 'NN'), ('of', 'IN'), ('an', 'DT'), ('unladen', 'JJ'), ('swallow', 'NN'), ('?', '.')]
        >>> tagger.close()

    This class communicates with the openNLP-tag jar file via pipes. When the
    tagger object is no longer needed, the close() method should be called to
    free system resources. The class supports the context manager interface; if
    used in a with statement, the close() method is invoked automatically:

        >>> with openNLPTaggerJava('en-pos-maxent.bin') as tagger:
        ...     tagger.tag('What is the airspeed of an unladen swallow ?'.split())
        ...
        [('What', 'WP'), ('is', 'VBZ'), ('the', 'DT'), ('airspeed', 'NN'), ('of', 'IN'), ('an', 'DT'), ('unladen', 'JJ'), ('swallow', 'NN'), ('?', '.')]
    """

    def __init__(self, path_to_model, path_to_jar=None,
                 encoding=_openNLP_charset, verbose=False):
        """
        Starts the opennlp-tools program  and establishes a connection with it.
        
        @param path_to_model: The model file.
        @param path_to_jar: The opennlp-tools jar file, which should be named opennlp-tools.jar.
        @param encoding: The encoding used by the model. C{unicode} tokens
            passed to the tag() and batch_tag() methods are converted to
            this charset when they are sent to openNLP-tag.
            The default is utf-8.

            This parameter is ignored for C{str} tokens, which are sent as-is.
            The caller must ensure that tokens are encoded in the right charset.
        """
        

        self._openNLP_jar = nltk.internals.find_jar(
                'opennlp-tools.jar', path_to_jar,
                searchpath=(), url=_openNLP_url,
                verbose=verbose)
        

        if not os.path.isfile(path_to_model):
            raise IOError("openNLP model file not found: %s" % model_file)
        self._openNLP_model = path_to_model
        self._encoding = encoding
        self._openNLP = Popen(["java","-Xmx1024m", "-jar",self._openNLP_jar, "POSTagger",self._openNLP_model],
                             shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        self._closed = False
        def __del__(self):
        	self.close()

    def close(self):
        """Closes the pipe to the openNLP process."""
        if not self._closed:
            self._openNLP.communicate()
            self._closed = True

    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def tag(self, tokens):
        """Tags a single sentence: a list of words.
        The tokens should not contain any newline characters.
        """
        for token in tokens:
            assert "\n" not in token, "Tokens should not contain newlines"
            if isinstance(token, unicode):
                token = token.encode(self._encoding)
            self._openNLP.stdin.write("%s " % token)
    	self._openNLP.stdin.write("\n")
        self._openNLP.stdin.flush()
        
        tagged_sentence = self._openNLP.stdout.readline().strip()
        tagged_tokens=[]
        for tagged_token in tagged_sentence.split():
            if "_" in tagged_token:
            	token,tag=tagged_token.split("_")
            else:
            	token=tagged_token
            	tag=None
            if isinstance(token, str):
            	token=token.decode(self._encoding)
            tagged_tokens.append((token, tag))
        
        return tagged_tokens

