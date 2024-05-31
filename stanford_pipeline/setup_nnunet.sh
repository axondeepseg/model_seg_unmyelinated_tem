#!/bin/bash
# This script sets up the nnUNet environment and runs the preprocessing and dataset integrity verification
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 PATH_TO_ORIGINAL_DATASET RESULTS_DIR [DATASET_ID] [DATASET_NAME]"
    exit 1
fi

config="2d"                     


PATH_TO_ORIGINAL_DATASET=$1
RESULTS_DIR=$(realpath $2)
dataset_id=${3:-010}
dataset_name=${4:-"TEM_STANFORD"}

echo "-------------------------------------------------------"
echo "Converting dataset to nnUNetv2 format"
echo "-------------------------------------------------------"

# Run the conversion script
python convert_bids_to_nnunetv2_format.py $PATH_TO_ORIGINAL_DATASET --TARGETDIR $RESULTS_DIR --DATASETID $dataset_id --DATASETNAME $dataset_name

# Set up the necessary environment variables
export nnUNet_raw="$RESULTS_DIR/nnUNet_raw"
export nnUNet_preprocessed="$RESULTS_DIR/nnUNet_preprocessed"
export nnUNet_results="$RESULTS_DIR/nnUNet_results"

echo "-------------------------------------------------------"
echo "Running preprocessing and verifying dataset integrity"
echo "-------------------------------------------------------"

nnUNetv2_plan_and_preprocess -d ${dataset_id} --verify_dataset_integrity -c ${config}