'''Extracts axon and myelin masks from nnunet raw predictions. This util writes 
binary masks for axon, myelin and unmyelinated axon classes. The axon and myelin
masks are also merged.
'''
import cv2
import argparse
import numpy as np
import json
from pathlib import Path

def extract_from_nnunet_prediction(pred, pred_path, class_name, class_value) -> str:
    '''
    Extracts the given class from the nnunet raw prediction, saves it in a 
    separate mask and return the path of the extracted mask.
    (Adapted from AxonDeepSeg #800 working branch)

    Parameters
    ----------
    pred : np.ndarray
        The raw prediction from nnunet with values 0, 1, 2, ...
    pred_path : pathlib.Path
        Path to the raw prediction file; We expect its filename to end 
        with '_seg-nnunet.png'
    class_name : str
        Name of the class to extract. e.g. 'axon', 'myelin', etc.
    class_value : int
        Value of the class in the raw prediction.

    Errors
    ------
    ValueError
        If the class value is not found in the raw prediction.
    ValueError
        If the raw nnunet prediction file does not end with '_seg-nnunet.png'.

    Returns
    -------
    new_fname : str
        Path to the extracted class mask saved.
    '''

    nnunet_suffix=Path('_seg-nnunet.png')

    if not np.any(pred == class_value):
        raise ValueError(f'Class value {class_value} not found in the raw prediction.')
    elif not pred_path.name.endswith(str(nnunet_suffix)):
        raise ValueError(f'Raw nnunet pred file does not end with "{nnunet_suffix}".')
    
    extraction = np.zeros_like(pred)
    extraction[pred == class_value] = np.iinfo(np.uint8).max
    new_fname = str(pred_path).replace(str(nnunet_suffix), f'_seg-{class_name}.png')
    cv2.imwrite(new_fname, extraction)

    return new_fname

def main():
    parser = argparse.ArgumentParser(description='Extract axon masks from nnunet pred.')
    parser.add_argument('input_dir', type=str, help='Path to the predictions folder.')
    
    dirname = Path(parser.parse_args().input_dir)
    assert dirname.exists(), f'Directory {dirname} does not exist.'

    # read classes
    with open(dirname / 'dataset.json', 'r') as f:
        mapping = json.load(f)['labels']
    classes_of_interest = ['uaxon', 'myelin', 'axon']

    for pred_path in dirname.glob('*_seg-nnunet.png'):
        pred = cv2.imread(str(pred_path), cv2.IMREAD_GRAYSCALE)
        masks = []
        for c in classes_of_interest:
            mask_path = extract_from_nnunet_prediction(pred, pred_path, c, mapping[c])
            masks.append(mask_path)
        print(f'Masks were extracted from {pred_path}. Merging axon and myelin masks.')
        # merge axon and myelin masks
        axon_mask = cv2.imread(masks[2], cv2.IMREAD_GRAYSCALE)
        myelin_mask = cv2.imread(masks[1], cv2.IMREAD_GRAYSCALE)
        merged_mask = np.zeros_like(axon_mask)
        merged_mask[axon_mask == 255] = 255
        merged_mask[myelin_mask == 255] = 128
        merged_mask_path = str(pred_path).replace('_seg-nnunet.png', '_seg-axonmyelin.png')
        cv2.imwrite(merged_mask_path, merged_mask)

        pred_path.unlink()

if __name__ == '__main__':
    main()