set -x

# in this experiment we create fake declensions, that is each lemma* in the
# language is arbitrarily assigned one of a few (e.g. 3) declension classes.
# the declension of a word determines the suffixes it takes for a given case
# (which is done in suffixes.py)

# *NOTE: for simplicity we assign all lemmas a declension, but in practice only nouns
# should be inflected for case

# PIPELINE:
#
# create lexicon from Europarl training data:
EPARL=data/eparl_train.conll
#cp /data/p286126/EuroNMT/data.-1/en.conll $EPARL
python2 create_lexicon.py --corpus_ud $EPARL --lexfile data/eparl.3decl
ln -s data/eparl.3decl lex_declensions.txt

# to create synthetic English variant with declensions:
# run main.py with --agreement-marker na-d-3dec

