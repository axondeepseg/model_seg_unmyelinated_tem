'''
This script evaluates the predictions of a model. For the predictions, this 
is the directory structure:

├── test/
    ├── sub-366A/
        ├── img_1_crop.png
        ├── img_2_crop.png
        ├── ...
    ├── sub-367A/
        ├── ...
    ├── ...

The labels should all be located in the same directory with suffix 
'_seg-uaxon-manual.png' and we assume there is a 1-1 correspondence between 
predictions and labels.
'''
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import cv2
import torch
from monai.metrics import DiceMetric, MeanIoU

def extract_binary_mask(pred_path):
    '''
    This function takes as input a 8-bit grayscale image with values 0 for bg and
    255 for unmyelintated axons. It returns a tensor with values 0 and 1. 
    '''
    mask = cv2.imread(pred_path, cv2.IMREAD_GRAYSCALE)[None]
    mask = np.where(mask > 200, 1, 0)
    mask = torch.from_numpy(mask).float()
    return mask

def main(pred_dir, label_dir, suffix='*_seg-uaxon.png'):
    
    metrics = [DiceMetric(), MeanIoU()]
    cols = ['Subject', 'Image', 'Dice', 'mIoU']
    df = pd.DataFrame(columns=cols)

    subjects = [x for x in Path(pred_dir).glob("sub-*") if x.is_dir()]
    for sub in subjects:
        sub_name = sub.name
        pred_files = list(sub.glob(suffix))
        for pred_file in pred_files:
            pred_mask = extract_binary_mask(str(pred_file))
            label_file = Path(label_dir) / str(pred_file.name).replace('_seg-uaxon.png', '_seg-uaxon-manual.png')
            assert label_file.exists(), f"Label file {label_file} does not exist"
            label_mask = extract_binary_mask(str(label_file))
            dice_metric = DiceMetric()
            dice = dice_metric([pred_mask], [label_mask])
            iou_metric = MeanIoU()
            iou = iou_metric([pred_mask], [label_mask])

            img_fname = str(pred_file.name).replace('_seg-uaxon.png', '.png')
            row = {
                'Subject': sub_name,
                'Image': img_fname,
                'Dice': dice.item(),
                'mIoU': iou.item()
            }
            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            # print(row)
    
    # export DataFrame to CSV file
    out_file = Path(pred_dir) / 'evaluation.csv'
    df.to_csv(out_file, index=False)
    print(f"Saved evaluation results to \n\t{out_file}\n for {len(df)} images.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pred_dir', type=str, required=True)
    parser.add_argument('-l', '--label_dir', type=str, required=True)
    args = parser.parse_args()
    main(args.pred_dir, args.label_dir)