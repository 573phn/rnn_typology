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
ERROR=$(cat <<-END
  jobscript.sh: Incorrect usage.
  Correct usage options are:
  - jobscript.sh [sov|svo|ovs|osv|vso|vos|random]
END
)

# Load Python module
module load Python/2.7.16-GCCcore-8.3.0

# Activate virtual environment
source "${DATADIR}"/env2/bin/activate

# Use Rafvogel script to reorder text
if [[ "$1" =~ ^(sov|svo|ovs|osv|vso|vos|random)$ ]]; then
  ./run.sh "$1"
else
  echo "${ERROR}"
  exit
fi
