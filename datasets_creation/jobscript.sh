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

# Set variables
agreement_marker="na-d"
order="sov"

# Zip English conll corpus for use with Ravfogel script
zip data/dev-penn-ud.zip data/en-corp.conll

# Use Rafvogel script to reorder text
if [[ "$1" =~ ^(sov|svo|ovs|osv|vso|vos|random)$ ]]; then
  python2 main.py --dataset dev \
                  --agreement-marker $agreement_marker \
                  --add-cases 0 \
                  --order "$1" \
                  --mark-verb 0
else
  echo "${ERROR}"
  exit
fi
