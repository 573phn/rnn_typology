#!/bin/bash
set -x

#SBATCH --job-name=rnn_typology
#SBATCH --output=slurm/slurm-%j.log
#SBATCH --time=1-12:00:00
#SBATCH --mem=8GB
#SBATCH --partition=regular

# Print arguments
echo "${@}"

# Set variables
DATADIR='/data/'"${USER}"'/rnn_typology'
ERROR=$(cat <<-END
  jobscript.sh: Incorrect usage.
  Correct usage options are:
  - jobscript.sh [sov|svo|ovs|osv|vso|vos|random|vso60rest8|vso30rest14|vos60rest8|vos30rest14] [none na-d na-s na-a] [0|1]
  (respectively: order add-cases? case-system print-txt?)
END
)

# Load Python module
module load Python/2.7.16-GCCcore-8.3.0

# Activate virtual environment
source "${DATADIR}"/env2/bin/activate

# Use Rafvogel script to reorder text
if [[ "$1" =~ ^(sov|svo|ovs|osv|vso|vos|random|vso60rest8|vso30rest14|vos60rest8|vos30rest14)$ ]] \
    && [[ "$2" =~ ^(none|na-d|na-s|na-a)$ ]] \
    && [[ "$3" =~ ^(0|1)$ ]]; then
  python2 main.py --dataset dev \
                  --order "$1" \
                  --add-cases 1 \
                  --agreement-marker "$2" \
                  --mark-verb 1 \
                  --print-txt $3

else
  echo "${ERROR}"
  exit
fi
