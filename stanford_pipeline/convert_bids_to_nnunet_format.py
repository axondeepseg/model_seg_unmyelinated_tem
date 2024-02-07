#!/usr/bin/env python3
"""
Prepares a new dataset for nnUNetv2, focusing on unmyelinated axon segmentation
in TEM data.

Features:
- Training Set Compilation: Includes all subjects with annotations in the 
  training set. nnUNetv2 will perform automatic cross-validation using these 
  annotated subjects.
- Testing Set Assignment: Allocates subjects without annotations to the 
  testing set, facilitating model performance evaluation on unseen data.
- Inspiration: The structure and methodology of this script is
  inspired by Armand Collin's work. The original script by Armand Collin can
  be found at:
  https://github.com/axondeepseg/model_seg_rabbit_axon-myelin_bf/blob/main/nnUNet_scripts/prepare_data.py
"""


__author__ = "Arthur Boschet"
__license__ = "MIT"


import argparse
import csv
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Literal

import cv2
import numpy as np


def create_directories(base_dir: str, subdirs: List[str]):
    """
    Creates subdirectories in a specified base directory.

    Parameters
    ----------
    base_dir : str
        The base directory where subdirectories will be created.
    subdirs : List[str]
        A list of subdirectory names to create within the base directory.
    """
    for subdir in subdirs:
        os.makedirs(os.path.join(base_dir, subdir), exist_ok=True)


def save_json(data: Dict, file_path: str):
    """
    Saves a dictionary as a JSON file at the specified path.

    Parameters
    ----------
    data : Dict
        Dictionary to be saved as JSON.
    file_path : str
        File path where the JSON file will be saved.
    """
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def process_images(
    datapath: Path,
    out_folder: str,
    particpant_to_sample_dict: Dict[str, List[str]],
    bids_to_nnunet_dict: Dict[str, int],
    dataset_name: str,
    is_test: bool = False,
):
    """
    Processes all image files in each subject's directory.

    Parameters
    ----------
    datapath : Path
        Path to the data directory.
    out_folder : str
        Output directory to save processed images.
    particpant_to_sample_dict : Dict[str, List[str]]
        Dictionary mapping participant IDs to sample IDs.
    bids_to_nnunet_dict : Dict[str, int]
        Dictionary mapping subject names to case IDs.
    dataset_name : str
        Name of the dataset.
    is_test : bool, optional
        Boolean flag indicating if the images are for testing, by default False.
    """
    folder_type = "imagesTs" if is_test else "imagesTr"
    image_suffix = "_0000"

    for subject in particpant_to_sample_dict.keys():
        for image in particpant_to_sample_dict[subject]:
            case_id = bids_to_nnunet_dict[str((subject, image))]
            image_path = os.path.join(
                datapath, subject, "micr", f"{subject}_{image}_TEM.png"
            )
            img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            fname = f"{dataset_name}_{case_id:03d}{image_suffix}.png"
            cv2.imwrite(os.path.join(out_folder, folder_type, fname), img)


def process_labels(
    datapath: Path,
    out_folder: str,
    particpant_to_sample_dict: Dict[str, List[str]],
    bids_to_nnunet_dict: Dict[str, int],
    dataset_name: str,
    label_type: Literal["axonmyelin", "myelin", "uaxon"] = "uaxon",
):
    """
    Processes label images from a list of subjects, matching each image with the label having the largest 'N' number.

    Parameters
    ----------
    datapath : Path
        Path to the data directory.
    out_folder : str
        Output directory to save processed label images.
    particpant_to_sample_dict : Dict[str, List[str]]
        Dictionary mapping participant IDs to sample IDs.
    bids_to_nnunet_dict : Dict[str, int]
        Dictionary mapping subject names to case IDs.
    dataset_name : str
        Name of the dataset.
    label_type : Literal["axonmyelin", "myelin", "uaxon"], optional
        Type of label to use. Options are 'axonmyelin', 'myelin', or 'uaxon'. Defaults to 'uaxon'.
    """
    label_type_to_divisor = {"axonmyelin": 127, "myelin": 255, "uaxon": 255}
    for subject in particpant_to_sample_dict.keys():
        for image in particpant_to_sample_dict[subject]:
            case_id = bids_to_nnunet_dict[str((subject, image))]
            label_path = os.path.join(
                datapath,
                "derivatives",
                "labels",
                subject,
                "micr",
                f"{subject}_{image}_TEM_seg-{label_type}-manual.png",
            )
            label = np.round(
                cv2.imread(str(label_path), cv2.IMREAD_GRAYSCALE)
                / label_type_to_divisor[label_type]
            )
            fname = f"{dataset_name}_{case_id:03d}.png"
            cv2.imwrite(os.path.join(out_folder, "labelsTr", fname), label)


def create_bids_to_nnunet_dict(file_path: Path) -> Dict[str, int]:
    """
    Creates a dictionary mapping unique (sample_id, participant_id) tuples to case IDs.

    Parameters
    ----------
    file_path : Path
        Path to the file containing the list of subjects.

    Returns
    -------
    Dict[str, int]
        Dictionary mapping unique (sample_id, participant_id) tuples to case IDs.
    """
    with open(file_path, "r") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip the header row
        bids_to_nnunet_dict = {}
        num = 1
        for row in reader:
            key = str((row[1], row[0]))  # (participant_id, sample_id)
            bids_to_nnunet_dict[key] = num
            num += 1
        return bids_to_nnunet_dict


def particpant_to_sample(file_path: Path) -> Dict[str, str]:
    """
    Creates a dictionary mapping participant IDs to sample IDs.

    Parameters
    ----------
    file_path : Path
        Path to the file containing the list of subjects.

    Returns
    -------
    Dict[str, str]
        Dictionary mapping participant IDs to sample IDs.
    """
    with open(file_path, "r") as file:
        reader = csv.reader(file, delimiter="\t")
        next(reader)  # Skip the header row
        particpant_to_sample_dict = {}
        for row in reader:
            participant_id = row[1]
            sample_id = row[0]
            if participant_id in particpant_to_sample_dict:
                particpant_to_sample_dict[participant_id].append(sample_id)
            else:
                particpant_to_sample_dict[participant_id] = [sample_id]
        return particpant_to_sample_dict


def main(args):
    """
    Main function to process dataset for nnUNet.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments containing DATAPATH and TARGETDIR.
    """
    dataset_name = args.DATASETNAME
    description = args.DESCRIPTION
    datapath = Path(args.DATAPATH)
    target_dir = Path(args.TARGETDIR)
    train_test_split_path = Path(args.SPLITJSON)
    label_type = args.LABELTYPE
    dataset_id = str(args.DATASETID).zfill(3)

    out_folder = os.path.join(
        target_dir, "nnUNet_raw", f"Dataset{dataset_id}_{dataset_name}"
    )
    create_directories(out_folder, ["imagesTr", "labelsTr", "imagesTs"])

    bids_to_nnunet_dict = create_bids_to_nnunet_dict(
        os.path.join(datapath, "samples.tsv")
    )

    with open(train_test_split_path, "r") as f:
        train_test_split_dict = json.load(f)
    train_participant_to_sample_dict = train_test_split_dict["train"]
    test_participant_to_sample_dict = train_test_split_dict["test"]

    dataset_info = {
        "name": dataset_name,
        "description": description,
        "labels": {"background": 0, "myelin": 1, "axon": 2}
        if label_type == "axonmyelin"
        else {"background": 0, "myelin": 1}
        if label_type == "myelin"
        else {"background": 0, "axon": 1},
        "channel_names": {"0": "rescale_to_0_1"},
        "numTraining": len(
            [
                image
                for images in train_participant_to_sample_dict.values()
                for image in images
            ]
        ),
        "numTest": len(
            [
                image
                for images in test_participant_to_sample_dict.values()
                for image in images
            ]
        ),
        "file_ending": ".png",
    }
    save_json(dataset_info, os.path.join(out_folder, "dataset.json"))

    process_images(
        datapath,
        out_folder,
        train_participant_to_sample_dict,
        bids_to_nnunet_dict,
        dataset_name,
        is_test=False,
    )
    process_labels(
        datapath,
        out_folder,
        train_participant_to_sample_dict,
        bids_to_nnunet_dict,
        dataset_name,
        label_type=label_type,
    )
    process_images(
        datapath,
        out_folder,
        test_participant_to_sample_dict,
        bids_to_nnunet_dict,
        dataset_name,
        is_test=True,
    )

    save_json(
        bids_to_nnunet_dict, os.path.join(target_dir, "subject_to_case_identifier.json")
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("DATAPATH", help="Path to the original dataset in BIDS format")
    parser.add_argument(
        "--TARGETDIR",
        default=".",
        help="Target directory for the new dataset, defaults to current directory",
    )
    parser.add_argument(
        "--DATASETNAME",
        default="TEM_STANFORD",
        help="Name of the new dataset, defaults to TEM_STANFORD",
    )
    parser.add_argument(
        "--DESCRIPTION",
        default="TEM unmyelinated axon segmentation dataset for nnUNetv2",
        help="Description of the new dataset, defaults to SEM segmentation dataset for nnUNetv2",
    )
    parser.add_argument(
        "--SPLITJSON",
        default="train_test_split.json",
        help="Path to the train_test_split.json file",
    )
    parser.add_argument(
        "--LABELTYPE",
        default="uaxon",
        help="Type of label to use. Options are 'axonmyelin', 'myelin', or 'uaxon'. Defaults to 'uaxon'",
    )
    parser.add_argument(
        "--DATASETID",
        default=10,
        type=int,
        help="ID of the dataset. This ID is formatted with 3 digits. For example, 1 becomes '001', 23 becomes '023', etc. Defaults to 10",
    )
    args = parser.parse_args()
    main(args)