#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Arianna Bisazza @RUG
# December 2020

import operator
#from sklearn.model_selection import train_test_split
import random
import agreement_markers
import argparse
from utils import *
import agreement_collector as ac
import sys

DECLENSION_RATIOS = [0.6, 0.3, 0.1] # splits list of lemmas in 3 random chunks with these ratios

def _arg2(pair):
    return pair[1]

            
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--corpus_ud', type=str, help = "parsed corpus in conll format", required = True, dest = "corpus")
    parser.add_argument('--lexfile', type=str, help = "filename of generated lexicon", required = True, dest = "lexfile")
    args = parser.parse_args()

    agreements =  {"nsubj": True, "dobj": True, "obj": True, "iobj": True}
    
    collector = ac.AgreementCollector(fname=args.corpus, agreements = agreements) 

    lexfileh = open(args.lexfile, "w")
    lem_freq = {}
    
    for i, sent in enumerate(tokenize(read(args.corpus))):
        #print(sent)
        #words = " ".join([tok[WORD] for tok in sent])
        #labels = " ".join([tok[LABEL] for tok in sent])
        if i%10000 == 0:
            print >> sys.stderr, "processed lines " + str(i)
            
        sent_info, deps = collector._get_deps(sent)
        words, tree_structure, lemmas, pos_tags, depths, labels = sent_info

        if not deps:
            # continue
            deps = {0: ''}  # Defining 'deps' so program leaves all sentences in

        #print(" ".join(words))
        #print(" ".join(lemmas))
        assert(len(lemmas)==len(words))
    
        for l in lemmas:
            lem_freq[l] = lem_freq.get(l,0) + 1
    
    ## end loop over corpus ##
    
    random.seed(18)
    
    lemmas = lem_freq.keys()
    n_lemmas = len(lemmas)
    random.shuffle(lemmas)
    
    ### assign declension randomly
    thresholds = []
    cum = 0
    for i in range(len(DECLENSION_RATIOS)-1):
        thresholds.append(int(DECLENSION_RATIOS[i] * n_lemmas -1) + cum)
        cum += thresholds[i]
    thresholds.append(n_lemmas)
    print(n_lemmas)           
    print(thresholds)
    
    lem_decl = {}
    d = 0
    for i in range(n_lemmas):
        if i>thresholds[d]:
            d += 1        
        lem_decl[lemmas[i]] = d+1

    ### sort by frequency and print
    sorted_by_freq = sorted(lem_freq.items(), key=_arg2, reverse=True)

    lexfileh.write("__LEMMA__\t__FREQ__\t__DECL__\n")
    for item in sorted_by_freq:
        l = item[0]
        lexfileh.write(l + "\t" + str(lem_freq[l]) + "\t" + str(lem_decl[l]) + "\n")

    #for item in lem_decl.items():
    #    lexfileh.write(item[0] + "\t" + str(item[1]) + "\n")
    
