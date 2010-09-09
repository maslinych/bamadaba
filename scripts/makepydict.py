#!/usr/bin/python
# -*- encoding: utf-8 -*-

import sys
sys.path.append('/home/kirill/src/mande')
import mandeist
import mandeist.orthography
import cPickle
import xml.etree.ElementTree as x
from nltk.corpus.reader import ToolboxCorpusReader
from nltk.corpus.util import LazyCorpusLoader
from contextlib import closing

propernames = LazyCorpusLoader(
        'bamana/propernames', ToolboxCorpusReader, '.*\.txt', encoding='utf-8')

bailleul = LazyCorpusLoader(
        'bamana/bailleul', ToolboxCorpusReader, r'bailleul.txt', encoding='utf-8')

lexicon = x.ElementTree(bailleul.xml('bailleul.txt'))

# hack provided for propernames to have gloss and ps tag
for file in propernames.fileids():
    for e in x.ElementTree(propernames.xml(file)).findall('record'):
        ge = x.Element('ge')
        ge.text = e.find('lx').text
        e.append(ge)
        ps = x.Element('ps')
        ps.text = 'n.prop'
        e.append(ps)
        lexicon.getroot().append(e)

wl_detone = {}

def normalize_bailleul(word):
    return u''.join([c for c in word if c not in u'.-'])

for entry in lexicon.findall('record'):
    ps = entry.findtext('ps')
    if ps != 'mrph':
        gloss = entry.findtext('ge')
        if not gloss:
            gloss = ''
        for e in entry:
            if e.tag in ['lx', 'le', 'va', 'vc']:
                lemma = e.text
                dictkey = mandeist.orthography.detone(normalize_bailleul(lemma.lower()))
                glosstree = mandeist.GlossTree()
                glosstree.append(mandeist.Gloss(u':'.join([lemma,ps,gloss])))
                wl_detone.setdefault(dictkey,[]).append(glosstree)
            if e.tag in ['mm']:
                wl_detone[dictkey][-1].append(mandeist.Gloss(e.text))

with closing(open('bamana.bdi', 'wb')) as outdict:
    cPickle.dump(wl_detone, outdict, -1)
