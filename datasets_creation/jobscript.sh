#!/bin/bash
#SBATCH --job-name=rnn_typology
#SBATCH --output=slurm/jobscript-%j.log
#SBATCH --time=3-00:00:00
#SBATCH --mem=64GB
#SBATCH --partition=regular

# Print arguments
echo "jobscript.sh" "${@}"

# Set variables
DATADIR='/data/'"${USER}"'/rnn_typology'
ERROR=$(cat <<-END
  jobscript.sh: Incorrect usage.
  Correct usage options are:
  - jobscript.sh [sov|svo|ovs|osv|vso|vos|random|vso60rest8|vso30rest14|vos60rest8|vos30rest14] [na-d|na-s|na-a] [0|1] [random_seed_int]
END
)
RE='^[0-9]+$'

# Load Python module
module load Python/2.7.16-GCCcore-8.3.0

# Activate virtual environment
source "${DATADIR}"/env2/bin/activate

# Use Rafvogel script to reorder text
if [[ "$1" =~ ^(sov|svo|ovs|osv|vso|vos|random|vso60rest8|vso30rest14|vos60rest8|vos30rest14)$ ]] \
    && [[ "$2" =~ ^(na-d|na-s|na-a)$ ]] \
    && [[ "$3" =~ ^(0|1)$ ]] \
    && [[ "$4" =~ $RE ]]; then

  if [[ "$5" == "control" ]]; then
    python2 main.py --dataset control \
                    --agreement-marker "$2" \
                    --add-cases 0 \
                    --order "$1" \
                    --mark-verb 0 \
                    --lemmatize 1 \
                    --print-txt "$3" \
                    --random-seed "$4"
  else
    python2 main.py --dataset dev \
                    --agreement-marker "$2" \
                    --add-cases 0 \
                    --order "$1" \
                    --mark-verb 0 \
                    --lemmatize 1 \
                    --print-txt "$3" \
                    --random-seed "$4"
  fi

else
  echo "${ERROR}"
  exit
fi
