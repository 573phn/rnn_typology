#!/usr/bin/env python
# -*- coding: utf-8 -*-

from utils import *
import copy
from collections import defaultdict, Counter
import random
import time
import agreement_markers
import csv
import suffixes
import pandas as pd
from getpass import getuser
import numpy as np

random.seed(5)
np.random.seed(5)

INDEX = 0
WORD = 1
LEMMA = 2
POS = 4
PARENT_INDEX = -4
LABEL = -3
PARENT = -1
PRINT = False

"""
This classs represents a node in a dependency parse tree. It offers methods for traversing the subtree rooted in the
node in a specific order, finding the number of a NP node and collecting verb arguments.
"""


class Node(object):
    def __init__(self, tok_id, word, lemma, pos, label):
        self.key = tok_id
        self.tok_id = tok_id
        self.word = word
        self.lemma = lemma
        self.pos = pos
        self.label = label
        self.is_verb = self.pos.startswith("V")
        self.lemmatized = False
        self.children = []

        self.parent = None
        self.parent_index = None
        self.number = None

        self.root = False
        self.depth = 0

    def __eq__(self, other):
        return self.key == other.key

    def __str__(self):
        """
        print the subtree rooted in self with indentation to express hierarchical sturcture.

        return: a string representing the sentence rooted in self.
        """
        parent = self.parent_index if self.parent_index else "ROOT"
        s = "   " * self.depth + str(
            self.tok_id) + "\t" + self.word + "\t" + self.lemma + "\t" + self.pos + "\t" + self.label + "\t" + str(
            parent) + "\n"
        for child in self.children:
            s += str(child)

        if self.root:
            s = s.strip()
        return s

    def get_tree_structure(self):
        pass

    def size(self):
        """
        return: number of nodes rooted in self.
        """
        if not self.children:
            return 1

        children_size = [c.size() for c in self.children]
        return sum(children_size) + 1

    def get_index(self):
        return self.tok_id

    def dfs(self, root, order=None):
        """
        perform a DFS traversal over the subtree rooted in self, in a spcific order.

        :param order:
                a string, representing the subject-object-verb order of the traversal, e.g. sov, vos.
                if none, assumes a canonical order.

        :return:
            a tuple (path, tree_structure):
                path:
                    an ordered list containing the nodes visited during the traversal.
                tree_structure:

                    a list containing a nested parantheses strings representing sentence structure
                    e.g. ["(", "(", "The", "man", ")", ...]
        """

        if order == "random":
            order = random.choice(["svo", "sov", "vso", "vos", "osv", "ovs"])
            
        if order == "vso60rest8":
            order = np.random.choice(["vso", "svo", "sov", "vos", "osv", "ovs"], p=[0.6]+[0.4/5]*5)
        if order == "vso30rest14":
            order = np.random.choice(["vso", "svo", "sov", "vos", "osv", "ovs"], p=[0.3]+[0.7/5]*5)

        if order == "vos60rest8":
            order = np.random.choice(["vos", "vso", "svo", "sov", "osv", "ovs"], p=[0.6]+[0.4/5]*5)
        if order == "vos30rest14":
            order = np.random.choice(["vos", "vso", "svo", "sov", "osv", "ovs"], p=[0.3]+[0.7/5]*5)
            
            

        if not self.is_verb or order is None:
            """
            the sentence tree is constructed in such a way that performing a DFS on the nodes ordered by their index
            yields the original linear order of elements.
            """
            nodes_sorted = sorted(self.children + [self], key=lambda node: node.get_index())
            nodes_in_order = nodes_sorted

        else:
            # if the node represents a verb, reorder its children to express the desired word order.
            node_to_char = lambda n: "v" if n.is_verb else "s" if (
                    n.label == "nsubj" or n.label == "nsubjpass") else "o"

            # find correct order for subject, object and verb nodes.
            children_without_so = []
            c_list = []
            for c in self.children:
                if c.label in ["aux", "auxpass", "prt", "neg", "compound:prt", "expl", "advmod"] or (
                        c.label == "mark" and c.word == "to"):
                    c_list.append(c)
            verb_and_auxiliaries = [self] + c_list
            verb_and_auxiliaries = sorted(verb_and_auxiliaries, key=lambda n: n.get_index())
            subjs, objs = [], []

            point_node = None

            for c in self.children:
                if (c.label == "nsubj" or c.label == "nsubjpass" or c.label == "csubj") and not (
                        c.pos == "WDT" or c.pos == "WP"):
                    subjs.append(c)
                elif (c.label == "dobj" or c.label == "ccomp" or c.label == "xcomp") and not (
                        c.pos == "WDT" or c.pos == "WP"):  # or (c.lemma == "''" or c.lemma == "``"):
                    objs.append(c)
                elif c.word != ".":
                    if c not in verb_and_auxiliaries:
                        children_without_so.append(c)
                else:
                    point_node = c

            children_without_so = sorted(children_without_so, key=lambda n: n.get_index())

            sov = [(subjs, "s"), (objs, "o"), (verb_and_auxiliaries, "v")]
            sov = sorted(sov, key=lambda (v, k): order.index(k))
            non_core_before, non_core_after = [], []

            for n in children_without_so:
                if n.get_index() < self.get_index():
                    non_core_before.append(n)
                else:
                    non_core_after.append(n)

            sov = [(non_core_before, "other_before")] + sov + [(non_core_after, "other_after")]

            nodes_in_order = []
            for (constit, _) in sov:
                for n in constit:
                    nodes_in_order.append(n)

            if point_node is not None:
                nodes_in_order.append(point_node)

        path = []
        tree_structure = ["("]

        for n in nodes_in_order:
            if n is not self:
                child_nodes, child_subtree = n.dfs(root, order)
                tree_structure.extend(child_subtree)
                path.extend(child_nodes)
            else:
                path.append(self)
                tree_structure.append(self.word)

        tree_structure.append(")")
        return path, tree_structure

    def add_children(self, children, edges, tree):
        """
        add children nodes to this node's list of children.

        :param children:
                a list, containing index of children nodes

        :param edges:
                a dictionary, mapping node_id to a list of its children ids.

        :param tree:
                a dictionary, mapping node ids to node objects
        """
        for tok_id in children:
            child = tree[tok_id]
            child.depth = self.depth + 1
            self.children.append(child)

            child.add_children(edges[tok_id], edges, tree)
            child.add_parent(self)

    def add_parent(self, node):
        self.parent = node
        self.parent_index = node.tok_id

    def set_number(self):
        """
            set self number according to word form and POS.
        """
        word, pos = self.word, self.pos

        word = word.lower()
        num = ""

        if not (pos in ["NN", "NNP", "NNS", "NNPS", "PRP"] or word in ["this", "that", "these", "those", "which",
                                                                       "who"]):
            self.number = None
            return

        if pos == "NN" or pos == "NNP":
            num = "sg"

        elif pos == "NNS" or pos == "NNPS":
            num = "pl"

        elif pos == "DT":
            if word in ["this", "that"]:
                num = "sg"
            else:
                num = "pl"

        elif pos == "PRP":
            if word in ["he", "him", "she", "her", "i", "it", "me"]:
                num = "sg"
            elif word in ["they", "we", "us", "them"]:
                num = "pl"
            else:  # you
                num = None

        elif pos == "WP" or pos == "WDT":
            # for who/which, check the referent's number.
            if self.parent is None or self.parent.parent is None:
                self.number = None
                return

            grandparent_pos = self.parent.parent.pos

            if grandparent_pos == "NN" or grandparent_pos == "NNP" or grandparent_pos in ["this", "that"]:
                num = "sg"
            else:
                num = "pl"

        self.number = num

    def collect_arguemnts(self, agreement_dict, agreements_to_collect, verbs_to_collect, argument_types):
        if (self.is_verb and self.label != "xcomp") and (verbs_to_collect is None or self.pos in verbs_to_collect):
            argument_types_to_collect = ["NN", "NNP", "JJ", "JJR", "JJS", "CD", "NNS", "NNPS", "PRP", "WDT", "WP", "DT"]

            if argument_types is not None:
                argument_types_to_collect = argument_types

            nuclear_children = (c for c in self.children if
                                c.label in agreements_to_collect and c.pos in argument_types_to_collect)

            for c in nuclear_children:
                child = c

                if c.pos == "WDT" or c.pos == "WP":
                    if self.label != "acl:relcl":
                        return dict()
                    else:
                        if self.parent.label in ["nsubj", "nsubjpass", "dobj"]:
                            continue
                        child = self.parent
                        child.label = c.label
                if child.number is not None:
                    agreement_dict[self.get_index()].append(child)

        for c in self.children:
            c.collect_arguemnts(agreement_dict, agreements_to_collect, verbs_to_collect, argument_types)

        return agreement_dict


def is_rcmod(node):
    return node.label == "acl:relcl"


def is_subj(node):
    return node.label == "nsubj"


class AgreementCollector(object):
    def __init__(self, mode="train", skip=1, fname=None, order=None, agreement_marker=None, agreements=None,
                 argument_types=None, verbs=None, most_common=200000, mark_verb=True, lemmatize_verbs=True, replace_uncommon=False,
                 add_gender=True, filter_no_att=False, filter_att=False, filter_obj=False, filter_no_obj=False,
                 filter_obj_att=False, filter_no_obj_att=False, print_txt=False):
        if agreements is None:
            agreements = dict()
        self.skip = skip
        self.fname = fname
        self.order = order
        self.agreement_marker = agreement_marker
        self.agreements = agreements
        self.most_common = most_common
        self.mark_verb = mark_verb
        self.lemmatize_verbs = lemmatize_verbs 
        self.mode = mode
        self.verbs = verbs
        self.argument_types = argument_types
        self.replace_uncommon = replace_uncommon
        self.add_gender = add_gender
        self.filter_no_att = filter_no_att
        self.filter_att = filter_att
        self.filter_obj = filter_obj
        self.filter_no_obj = filter_no_obj
        self.filter_obj_att = filter_obj_att
        self.filter_no_obj_att = filter_no_obj_att
        self.print_txt = print_txt

        self._load_freq_dict()

        if self.add_gender:
            self.w2g = dict()
        # self._add_gender()

        if not any(agreements.values()):
            raise Exception("Expecting at least one verb-argument agreement to collect.")

        if self.order is not None and self.order not in ["svo", "sov", "vso", "vos", "osv", "ovs", "random", "vso60rest8", "vso30rest14", "vos60rest8", "vos30rest14"]:
            raise Exception("Unrecognized order order.")

    def _load_freq_dict(self):
        vocab = set()

        with open("voc.txt", "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            word, freq = line.strip().split("\t")
            vocab.add(word)

            if self.replace_uncommon and i > self.most_common:
                break

        self.vocab = vocab

    def _add_gender(self):
        w2g = dict()

        for w in self.vocab:
            if random.random() < 0.5:
                w2g[w] = 0
            else:
                w2g[w] = 1
        self.w2g = w2g

    def _fix_copulas(self, node):
        if node.label == "cop":
            parent = node.parent
            for c in parent.children:
                if c.label == "nsubj" or c.label == "nsubjpass":
                    if node.word in ["is", "are", "'s", "'re", "was", "were"]:
                        c.parent = node
                        node.children.append(c)
                        parent.children.remove(c)
                    else:
                        continue

        for c in node.children:
            self._fix_copulas(c)

    def _sent_to_tree(self, sent):
        """
        convert a sentence to a rooted tree object.
        """
        tree = dict()
        edges = defaultdict(list)

        for tok in sent:
            tok_id = int(tok[INDEX]) - 1
            word = tok[WORD]
            lemma = tok[LEMMA]
            pos = tok[POS]
            label = tok[LABEL]
            parent = int(tok[PARENT_INDEX]) - 1
            node = Node(tok_id, word, lemma, pos, label)

            if self.add_gender:
                if word in self.w2g:
                    gender = self.w2g[word]

                else:
                    gender = random.choice(["0", "1"])
                    self.w2g[word] = gender

                node.gender = gender

            if label.lower() == "root":
                root = node
                node.root = True
                tree['root'] = node
            root_id = tok_id

            tree[tok_id] = node
            edges[parent].append(tok_id)

        root_children = edges[root.tok_id]
        root.add_children(root_children, edges, tree)

        for node in tree.values():
            node.set_number()

        self._fix_copulas(root)

        return tree

    def _get_nodes_between(self, node1_index, node2_index, dfs_ordered_nodes):  # in dfs order
        if node2_index < node1_index:
            node2_index, node1_index = node1_index, node2_index
        return dfs_ordered_nodes[node1_index + 1:node2_index]

    def _add_cases(self, nodes_and_cases, verb_arguments):
        """
        add case suffixes to the words represented by the verb node and its argument nodes.

        :param nodes_and_cases:

            a list of tuples (node, suffix), containing a verb node and its argument nodes.
            this list is the output of the agreement marker.
        """
        for (node, suffix) in nodes_and_cases:
            if not node.is_verb:
                node.word = node.lemma.lower()

            else:
                verb_and_children = node.children[:]
                verb_and_children.append(node)

                for n in verb_and_children:
                    if node.word == node.pos:
                        continue

                    if n.word in ["was", "were"]:
                        n.word = "was"

                    elif n.word in ["have", "has"]:
                        n.word = "have"

                    elif n.word in ["is", "are"]:
                        n.word = "is"

                    elif (n.pos == "VBZ" or n.pos == "VBP") and not n.lemmatized:
                        n.word = n.lemma
                        n.lemmatized = True

            if (not node.is_verb) or self.mark_verb:
                node.word += suffix

    def _get_deps(self, sent):
        tree = self._sent_to_tree(sent)
        root = tree['root']
        """
        print "===================================="
        if PRINT:
            print root
        """
        for n in tree.values():
            n.word = n.word.lower()

            if n.word not in self.vocab and self.replace_uncommon:
                n.word = n.pos
                if self.add_gender:
                    n.word += str(self.w2g[n.word])

        agreement_dict = defaultdict(list)
        agreements_to_collect = [k for (k, v) in self.agreements.items() if v]

        if "nsubj" in agreements_to_collect:
            agreements_to_collect.append("nsubjpass")

        root.collect_arguemnts(agreement_dict, agreements_to_collect, self.verbs, self.argument_types)

        nodes_dfs, tree_structure = root.dfs(root, self.order)

        depths = []
        pos_tags = []
        lemmas = []
        labels = []

        for n in nodes_dfs:
            depths.append(str(n.depth))
            pos_tags.append(n.pos)
            lemmas.append(n.lemma)
            labels.append(n.label)

        deps = defaultdict(dict)

        for verb_id in agreement_dict.keys():
            verb_arguments = agreement_dict[verb_id]
            verb_node = tree[verb_id]
            verb_index = nodes_dfs.index(verb_node)

            # lemmatization of verbs happens here unless disabled by option '-lemmatize 0'
            if self.agreement_marker and self.lemmatize_verbs :
                nodes_and_cases = self.agreement_marker.mark(verb_node, verb_arguments, add_gender=self.add_gender,
                                                             mark_auxiliary=False)
                self._add_cases(nodes_and_cases, verb_arguments)


            for argument_node in verb_arguments:

                argument_index = nodes_dfs.index(argument_node)

                between = self._get_nodes_between(verb_index, argument_index, nodes_dfs)
                nouns_between = [n for n in between if n.pos in ['NN', 'NNS']]
                dis = len(between) + 1
                has_rel = 1 if any(map(is_rcmod, between)) else 0
                has_subj = 1 if any(map(is_subj, between)) else 0
                attractors = [n for n in nouns_between if n.number is not None and n.number != argument_node.number]
                num_attractors = len(attractors)
                attractors_words = [n.word for n in nouns_between if
                                    n.number is not None and n.number != argument_node.number]

                other_arguments = [arg for arg in verb_arguments if arg != argument_node]
                children_of_other_arguments = [arg.children for arg in other_arguments]
                non_argument_attractors = []
                for att in attractors:
                    is_argument = False
                    for childlist in children_of_other_arguments:
                        if att in childlist and att.label == "compound":
                            is_argument = True
                    for other_argument in other_arguments:
                        if att is other_argument:
                            is_argument = True
                    if not is_argument:
                        non_argument_attractors.append(att)

                num_non_argument_attractors = len(non_argument_attractors)

                if argument_node.label == "nsubjpass":
                    label = "nsubj"
                else:
                    label = argument_node.label

                deps[verb_index][label] = {"index": argument_index,
                                           "number": argument_node.number,
                                           "distance": str(dis),
                                           "has_rel": str(has_rel),
                                           "has_subj": str(has_subj),
                                           "number_attractors": str(num_attractors),
                                           "pos": argument_node.pos,
                                           "attractors_words": " ".join(attractors_words),
                                           "number_non_argument_attractors": str(num_non_argument_attractors)}

        deps = {k: v for (k, v) in deps.iteritems() if "nsubj" in v or "nsubjpass" in v}
        words = [n.word for n in nodes_dfs]
        sent_info = (words, tree_structure, lemmas, pos_tags, depths, labels)
        return sent_info, deps

    def collect_agreement(self):
        df = pd.DataFrame(columns=["en_" + self.order])
        sents = []
        t = time.time()

        batches = 0
        sents_counter = 0
        count_iobj = 0.

        if PRINT:
            print "-----------------------------"

        textfilename_orig = "../datasets/deps_orig" + ".txt"
        textfilename = "../datasets/deps_" + self.order + "_" + self.agreement_marker.get_type() + ".txt"
        textfile_orig = None
        textfile = None
        if self.print_txt:
            textfile_orig = open(textfilename_orig, "w")
            textfile = open(textfilename, "w")

        for i, sent in enumerate(tokenize(read(self.fname))):
            words = " ".join([tok[WORD] for tok in sent])
            labels = " ".join([tok[LABEL] for tok in sent])

            has_iobj = "iobj" in labels
            if has_iobj:
                count_iobj += 1
            if not sent:
                continue
            if i % self.skip != 0:
                continue

            sent_info, deps = self._get_deps(sent)
            words, tree_structure, lemmas, pos_tags, depths, labels = sent_info

            if not deps:
                # continue
                deps = {0: ''}  # Defining 'deps' so program leaves all sentences in

            verb_index = random.choice(deps.keys())
            verb_dep = deps[verb_index]

            sent_dict = dict()
            sent_dict["sent_words"] = " ".join(words)
            sent_dict["sent_structure"] = " ".join(tree_structure)
            sent_dict["sent_pos"] = " ".join(pos_tags)
            sent_dict["sent_lemmas"] = " ".join(lemmas)
            sent_dict["sent_labels"] = " ".join(labels)
            sent_dict["sent_depths"] = " ".join(depths)
            sent_dict["verb_index"] = str(verb_index)
            sent_dict["original_sent"] = " ".join([tok[WORD] for tok in sent])
            sent_dict["verbs_count"] = len([p for p in pos_tags if p.startswith("v") or p.startswith("V")])

            props = ["index", "number", "distance", "has_rel", "has_subj", "number_attractors",
                     "number_non_argument_attractors", "pos", "attractors_words"]

            for l in self.agreements:
                for prop in props:
                    val = verb_dep[l][prop] if l in verb_dep else "-"
                    sent_dict[l + "_" + prop] = val

            if self.filter_no_att and sent_dict["nsubj_number_attractors"] == "0":
                continue
            if self.filter_att and sent_dict["nsubj_number_attractors"] != "0":
                continue
            if self.filter_obj and "dobj" in sent_dict["sent_labels"]:
                continue
            if self.filter_no_obj and sent_dict["dobj_number"] == "-":
                continue
            if self.filter_obj_att and sent_dict["dobj_number"] != "-" and sent_dict["dobj_number"] != sent_dict[
                    "nsubj_number"]:
                continue
            if self.filter_no_obj_att and (
                    sent_dict["dobj_number"] == "-" or sent_dict["dobj_number"] == sent_dict["nsubj_number"]):
                continue

            if PRINT:
                # print sent_dict["dobj_number"], sent_dict["nsubj_number"]
                print 'Original:', sent_dict["original_sent"]
                print 'Modified:', sent_dict["sent_words"]
                print "-----------------------------"

            if self.print_txt:
                textfile_orig.write(sent_dict["original_sent"].lower() + "\n")
                textfile.write(sent_dict["sent_words"] + "\n")

            df.loc[i] = sent_dict["sent_words"]
            

            sents.append(sent_dict)
            sents_counter += 1

            if i % 1 == 0:
                if batches == 0:
                    to_write = [sorted(sents[0].keys())]
                    fname = "deps_" + self.order + ".csv"
                    write_to_csv(to_write, mode="w", fname=fname)
                else:
                    to_write = [[v for (k, v) in sorted(sent_dict.items(), key=lambda (k, v): k)] for sent_dict in
                                sents]
                    write_to_csv(to_write, mode="a", fname=fname)
                    sents = []

                batches += 1

        # save DataFrame to .h5 file
        df.to_hdf("/data/{}/rnn_typology/".format(getuser())+"/en_" + self.order + ".h5", key=self.order, mode="w")
        
        # open saved .h5 file, save its contents as .json (workaround to be able to open it in Python 3 later)
        df = pd.read_hdf("/data/{}/rnn_typology/".format(getuser())+"/en_" + self.order + ".h5")
        json_string = df.to_json(compression="gzip")
        with open("/data/{}/rnn_typology/".format(getuser())+"/en_" + self.order + ".json.gz", "w") as fp:
            fp.write(json_string)

        if self.print_txt:
            textfile_orig.close()
            textfile.close()

        print "Done. Dataset saved in '/data/{}/rnn_typology/".format(getuser())+"'"
