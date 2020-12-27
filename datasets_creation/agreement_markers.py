#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import suffixes

"""
An abstract class that adds agreement and case marks to sentence elements (verbs and their arguments).

Case system:

                        SG          PL
    
    SUBJECT/ERGATIVE            ~           ^
    
    OBJECT/ABSOLUTIVE           #           *
    
    INDIRECT OBJECT / DATIVE        @           &
"""

"""
NOTE on verb suffixes:
        # verbs used to be marked by both subj and obj agreement
        # now it depends on the chosen Case System:
        # - deterministic system (na-d)         => marks verbs w/ both subj and obj (polypersonal agreement)
        # - argument-marking-only system (na-a) => marks verbs w/ subj agreement only (inspired by Russian)
        #
        # NOTE: other case systems have not been modified according (i.e. mark polypersonal agreement by default) 
"""

class AgreementMarker(object):

    def __init__(self, add_cases, verb_agr_subj_only = False):
    
        """
        
        :param add_cases:
        
            a boolean. If true, adds case suffixes to NPs.
        """
        
        self.add_cases = add_cases
        self.verb_agr_subj_only = verb_agr_subj_only
        self.name = "none"
        
    def mark(self, verb_node, agreement_nodes, add_gender = False, mark_auxiliary = True):
    
        cases = []
        is_transitive = any(((n.label == "dobj" or n.label == "obj") for n in agreement_nodes))
        verb_suffix = []
        
        for agreement_node in agreement_nodes:
        
            case = self.get_case(verb_node, agreement_node, is_transitive)
            gender = "" if not add_gender else agreement_node.gender
            
            if (not self.verb_agr_subj_only) or \
                agreement_node.label == "nsubj" or \
                agreement_node.label == "nsubjpass" or agreement_node.label == "nsubj:pass":
                    verb_suffix.append((case, gender))

            if self.add_cases:              
                cases.append((agreement_node, case))

        #print ("D0:", verb_suffix)
        verb_suffix = list(dict.fromkeys(verb_suffix))
        #print ("D1:", verb_suffix)
        verb_suffix = sorted(verb_suffix, key = lambda (case, gender): case)
        #print ("D2:", verb_suffix)
        # HACKY: in case of 2 suffixes with same case but different number, only keep the first one (.pl)
        # (the problem of many suffixes seem to happen because of incorrect automatic parses with multiple subjects)
        prev_case = ""
        newlist = []
        for s in verb_suffix:
            s_case = s[0][:-3]
            #print s_case
            if prev_case != s_case:
                newlist.append(s)
            prev_case = s_case
        verb_suffix = newlist
        #print ("D3:", verb_suffix)
        verb_suffix = "".join([case + gender for (case, gender) in verb_suffix])
        #print()
        
        found = False
        
        if mark_auxiliary:
            
            verb_children = verb_node.children
            auxiliaries = [c for c in verb_children if c.label == "aux" or c.label == "auxpass" or c.label == "aux:pass"]
            if len(auxiliaries) > 0:
                found = True
                last = auxiliaries[-1]
                cases.append((last, verb_suffix))
                
        if not found:
        
            cases.append((verb_node, verb_suffix))
        
        return cases
            
    def get_case(self, verb_node, agreement_node, is_transitive):
    
        raise NotImplementedError

    def get_name(self):
            return self.name
    
    #load lexicon of lemmas with frequency and declension
    def _load_freq_decl_dict(self):
        vocab = {}

        with open("lex_declensions.txt", "r") as f:
            lines = f.readlines()

        assert(lines[0].strip() == "__LEMMA__	__FREQ__	__DECL__")
        for i, line in enumerate(lines[1:]):
            word, freq, decl = line.strip().split("\t")
            vocab[word] = (int(freq), int(decl))

        return vocab  
                
        
class NominativeAccusativeMarker(AgreementMarker):

    def __init__(self, add_cases = False, verb_agr_subj_only = False):
        super(NominativeAccusativeMarker, self).__init__(add_cases,verb_agr_subj_only)
        if self.add_cases:
            self.name = "na-d"
        
    def get_case(self, verb_node, agreement_node, is_transitive):

        #print "adding case to node ", agreement_node.word
        if agreement_node.label == "nsubj" or agreement_node.label == "nsubjpass" or agreement_node.label == "nsubj:pass":

            case = suffixes.nsubj_sg if agreement_node.number == "sg" else suffixes.nsubj_pl

        elif agreement_node.label == "dobj" or agreement_node.label == "obj":
            
            case = suffixes.dobj_sg if agreement_node.number == "sg" else suffixes.dobj_pl
            
        elif agreement_node.label == "iobj":
                
            case = suffixes.iobj_sg if agreement_node.number == "sg" else suffixes.iobj_pl

        return case


class NominativeAccusativeMarker3Decl(AgreementMarker):
    def __init__(self, add_cases = False, verb_agr_subj_only = False):
        super(NominativeAccusativeMarker3Decl, self).__init__(add_cases,verb_agr_subj_only)
        if self.add_cases:
            self.name = "na-d-3dec"
            self.lex_decl = self._load_freq_decl_dict()
            print(len(self.lex_decl.keys()))

    def get_case(self, verb_node, agreement_node, is_transitive):

        #print "adding case to node:", agreement_node.word
        #print(agreement_node.lemma)  
        #print(agreement_node.number)  

        role = ""
        if agreement_node.label == "nsubj" or agreement_node.label == "nsubjpass" or agreement_node.label == "nsubj:pass":
            role = "nsubj"
        elif agreement_node.label == "dobj" or agreement_node.label == "obj":
            role = "dobj"
        elif agreement_node.label == "iobj":
            role = "iobj"
        
        case_suffix = suffixes.get_surface(role, agreement_node.number, False, agreement_node.lemma, self.lex_decl)
        #print(case_suffix)
        
        return case_suffix
        
class AmbigiousNominativeAccusativeMarker(AgreementMarker):

    def __init__(self, add_cases = False, verb_agr_subj_only = False):
        super(AmbigiousNominativeAccusativeMarker, self).__init__(add_cases,verb_agr_subj_only)
        if self.add_cases:
            self.name = "na-s"

    def get_case(self, verb_node, agreement_node, is_transitive):

        #print "adding case to node ", agreement_node.word
         
        if (agreement_node.label == "nsubj" or agreement_node.label == "nsubjpass" or agreement_node.label == "nsubj:pass"):
                    
            case = suffixes.nsubj_sg if agreement_node.number == "sg" else suffixes.nsubj_pl
                    
        elif agreement_node.label == "dobj" or agreement_node.label == "obj":
            
            case = suffixes.dobj_sg if agreement_node.number == "sg" else suffixes.nsubj_sg
            
        elif agreement_node.label == "iobj":
                            
            case = suffixes.iobj_sg if agreement_node.number == "sg" else suffixes.iobj_pl

        return case
        
class ErgativeAbsolutiveMarker(AgreementMarker):

    def __init__(self, add_cases=False, verb_agr_subj_only = False):
        super(ErgativeAbsolutiveMarker, self).__init__(add_cases,verb_agr_subj_only)
        if self.add_cases:
            self.name = "ea-d"
        
    def get_case(self, verb_node, agreement_node, is_transitive):

        is_subj = agreement_node.label == "nsubj" or agreement_node.label == "nsubjpass" or agreement_node.label == "nsubj:pass"
        
        if (not is_transitive and is_subj) or agreement_node.label == "dobj" or agreement_node.label == "obj":
                
            case = suffixes.dobj_sg if agreement_node.number == "sg" else suffixes.dobj_pl
                    
        elif is_transitive and is_subj:
            
            case = suffixes.nsubj_sg if agreement_node.number == "sg" else suffixes.nsubj_pl
            
        elif agreement_node.label == "iobj":
            
            case = suffixes.iobj_sg if agreement_node.number == "sg" else suffixes.iobj_pl
        
        return case
        
class AmbigiousErgativeAbsolutiveMarker(AgreementMarker):

    def __init__(self, add_cases=False, verb_agr_subj_only=False):
        super(AmbigiousErgativeAbsolutiveMarker, self).__init__(add_cases,verb_agr_subj_only)
        if self.add_cases:
            self.name = "ea-s"

    def get_case(self, verb_node, agreement_node, is_transitive):

        is_subj = agreement_node.label == "nsubj" or agreement_node.label == "nsubjpass" or agreement_node.label == "nsubj:pass"
        
        if (not is_transitive and is_subj) or agreement_node.label == "dobj" or agreement_node.label == "obj":
                
            case = suffixes.dobj_sg if agreement_node.number == "sg" else suffixes.dobj_pl
                    
        elif is_transitive and is_subj:
            
            case = suffixes.dobj_pl if agreement_node.number == "sg" else suffixes.nsubj_pl
            
        elif agreement_node.label == "iobj":
                
            case = suffixes.iobj_sg if agreement_node.number == "sg" else suffixes.iobj_pl
        
        return case

class ArgumentPresenceMarker(AgreementMarker):

    def __init__(self, add_cases=False, verb_agr_subj_only=True):
        super(ArgumentPresenceMarker, self).__init__(add_cases,verb_agr_subj_only)
        if self.add_cases:
            self.name = "na-a"
        
    def get_case(self, verb_node, agreement_node, is_transitive):

        case = suffixes.arg_sg if agreement_node.number == "sg" else suffixes.arg_pl
        
        return case

