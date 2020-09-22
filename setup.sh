#!/bin/bash

# Load Python module
module load Python/2.7.16-GCCcore-8.3.0

# Set data location
DATADIR='/data/'"${USER}"'/rnn_typology'

# Prepare /data directories, ignore warning in case it already exists
mkdir -p "${DATADIR}"

# Create virtual environment
python2 -m virtualenv "${DATADIR}"/env2

# Activate virtual environment
source "${DATADIR}"/env2/bin/activate

# Upgrade pip (inside virtual environment)
pip2 install --upgrade pip==19.2.3

# Install required packages (inside virtual environment)
pip2 install numpy==1.16.6 dynet==2.0.3 pandas==0.24.2 tables==3.5.2 pyarrow==0.16.0
