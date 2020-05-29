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

suffixes = [nsubj_sg, nsubj_pl, dobj_sg, dobj_pl, iobj_sg, iobj_pl]

def is_nsubj(suffix):
    return suffix == nsubj_sg or suffix == nsubj_pl

def is_dobj(suffix):
    return suffix == dobj_sg or suffix== dobj_pl

def is_iobj(suffix):
    return suffix == iobj_sg or suffix== iobj_pl
