#!/bin/bash

# Directory containing the tar.bz2 files
BASE_DIR="silicon_data/2_Electronic_Stopping/H_Si/LDA_H*/v*"

# Find all unique directories containing output.tar.bz2 files
dirs=$(find $BASE_DIR -type f -name "output.tar.bz2" -exec dirname {} \; | sort -u)

# Loop through each directory
for dir in $dirs; do
  # Loop through each tar.bz2 file in the directory
  for file in "$dir"/output.tar.bz2; do
    if [ -f "$file" ]; then
      # Extract the file
      tar -xjf "$file" -C "$dir"
      echo "Unzipped: $file"
    else
      echo "No .tar.bz2 files found in $dir"
    fi
  done
done


