#!/bin/bash
#SBATCH --job-name=rnn_typology
#SBATCH --output=slurm/slurm-%j.log
#SBATCH --time=10:00
#SBATCH --mem=8GB
#SBATCH --partition=regular

# Print arguments
echo "${@}"

# Set variables
DATADIR='/data/'"${USER}"'/rnn_typology'

# Load Python module
module load Python/2.7.16-GCCcore-8.3.0

# Activate virtual environment
source "${DATADIR}"/env2/bin/activate

# Run script
echo "Now running collect_vocab.py:"
python2 collect_vocab.py
echo "Now running main.py:"
python2 main.py
