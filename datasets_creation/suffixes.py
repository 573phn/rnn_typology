import sys

#explicit = False
explicit = True 

nsubj_sg = "kar" if not explicit else ".nsubj.sg"
nsubj_pl = "kon" if not explicit else ".nsubj.pl"
dobj_sg = "kin" if not explicit else ".dobj.sg"
dobj_pl = "ker" if not explicit else ".dobj.pl"
iobj_sg = "kan" if not explicit else ".iobj.sg"
iobj_pl = "kre" if not explicit else ".iobj.pl"

# following are for Argument Marking only languages:
arg_sg = "kaz" if not explicit else ".arg.sg"
arg_pl = "koz" if not explicit else ".arg.pl"

# with 3 different (arbitrary) declensions (the array index is the declension of the noun)
surfaces_decl = {
    'nsubj_sg':[".nsubj.sg","kar","par","pa"],
    'nsubj_pl':[".nsubj.pl","kon","pon","po"],
    'dobj_sg':[".dobj.sg","kin","it","kit"],
    'dobj_pl':[".dobj.pl","ker","et","ket"],
    'iobj_sg':[".iobj.sg","ken","kez","ke"],
    'iobj_pl':[".iobj.pl","kre","kr","re"],
    'arg_sg':[".arg.sg","kaz","kz","ka"],
    'arg_pl':[".arg.pl","koz","kz","ko"],
}

suffixes = [nsubj_sg, nsubj_pl, dobj_sg, dobj_pl, iobj_sg, iobj_pl]

def get_surface(case, number, explicit_form, lemma, lex):
    tag = case + "_" + number
    decl_index = None
    if explicit_form:
        decl_index = 0  
    else:
        decl_index = 1    # DEFAULT to 1st declension (if lemma not in lexicon) 
    if lemma and lex:
        if lemma in lex:
            decl_index = lex[lemma][1]  # expected value: tuple of (freq, decl)
            #print "decl: ", decl_index
        else:
            print >> sys.stderr, "lemma not in lex:" + lemma + "using default declension"
    return surfaces_decl[tag][decl_index]


def is_nsubj(suffix):
    return suffix == nsubj_sg or suffix == nsubj_pl

def is_dobj(suffix):
    return suffix == dobj_sg or suffix== dobj_pl

def is_iobj(suffix):
    return suffix == iobj_sg or suffix== iobj_pl

def load_lex(fname):
    for line in read(fname):
        print(line)
        # TODO!


    
