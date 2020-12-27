# in this experiment we create fake declensions, that is each lemma* in the
# language is arbitrarily assigned to one of a few declension classes.
# the declension of a word determines the suffixes it takes for a given case
# (which is done in suffixes.py

# * for simplicity we assign all lemmas a declension, but in practice only nouns
# should be inflected for case

# PIPELINE:

# create lexicon from Europarl training data:
python2 create_lexicon.py --corpus_ud data/XXXX --lexfile data/eparl.3decl
ln -s data/eparl.3decl lex_declensions.txt

# to create synthetic English variant with declensions:
# run main.py with --agreement-marker na-d-3decl

