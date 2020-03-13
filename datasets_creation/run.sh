#!/bin/bash

# Print arguments
echo "${@}"

ERROR=$(cat <<-END
  run.sh: Incorrect usage.
  Correct usage options are:
  - run.sh [sov|svo|ovs|osv|vso|vos|random]
END
)

# Zip English conll corpus for use with Ravfogel script
zip data/dev-penn-ud.zip data/en-corp.conll

if [[ "$1" =~ ^(sov|svo|ovs|osv|vso|vos|random)$ ]]; then
  python2 main.py --dataset dev \
                  --agreement-marker "na-d" \
                  --add-cases 0 \
                  --order "$1" \
                  --mark-verb 0
else
  echo "${ERROR}"
  exit
fi