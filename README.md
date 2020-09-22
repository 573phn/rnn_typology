# RNNs and syntactic variability

This repository contains a modified version of the code for the creation of the synthetic langauges used in the paper "[Studying the inductive biases of RNNs
with synthetic variations of natural languages](https://arxiv.org/abs/1903.06400)" (accepted paper in NAACL 2019).

### Dataset Creation

The `dataset_creation` directory contains the code for creating verb-argument agreement datasets for synthetic versions of English.

The arguments specified in `main.py` allow controlling for various parameters, such as with which arguments the verb agrees, whether NPs are marked for nuclear cases, which case system to use, and what would be the verb-subject-object order. For example, the input sentence "they say the broker took them out for lunch frequently", when converted to OVS word order, yields the sentence "them took out frequently the broker for lunch say they".

### Running the code on Peregrine

1. Run `./setup.sh` to setup a virtual environment and install the required packages
2. Run `sbatch jobscript.sh [sov|svo|ovs|osv|vso|...] [na-d na-s na-a] [0|1] [random_seed_int]` or `jobscript_cases.sh [sov|svo|ovs|osv|vso|...] [na-d na-s na-a] [0|1] [random_seed_int]`, this will
   * let the Ravfogel code reorder the data contained in `datasets_creation/data/dev-penn-ud.zip`
   * write output data to `/data/$USER/rnn_typology/deps_[wo].csv`, `/data/$USER/rnn_typology/en_[wo][agreement-marker]seed[int].json.gz` and `/data/$USER/rnn_typology/en_[wo][agreement-marker]seed[int].ftr` ([Feather file format](https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#feather))
