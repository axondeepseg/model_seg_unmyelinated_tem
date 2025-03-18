'''Reads myelinated + unmyelinated axon morphometric files and count axons.
'''
from pathlib import Path
from tqdm import tqdm
import argparse
import pandas as pd
import skimage.measure as skm
import cv2

def main():
    parser = argparse.ArgumentParser(description='Aggregate morphometrics.')
    parser.add_argument('input_dir', type=str, help='Path to the folder containing all morphometric files.')
    parser.add_argument('-m', '--mask', action='store_true', default=False, help='Toggles mask mode: use masks instead of .xlsx to count axons.')
    parser.add_argument('output_name', type=str, help='Name of the output file.')

    args = parser.parse_args()
    input_dir = Path(args.input_dir)
    out_name = args.output_name
    mask_mode = args.mask
    assert input_dir.exists(), f'Directory {input_dir} does not exist.'

    # find images except for the masks
    mask_suffixes = (
        '_seg-axon.png', '_seg-myelin.png', '_seg-uaxon.png', '_uaxon_index.png', 
        '_seg-axonmyelin.png', '_axonmyelin_index.png', '_index.png', '_seg-axonmyelin-manual.png',
        '_seg-uaxon-manual.png'
    )
    inputs = [f for f in input_dir.glob('*.png') if not f.name.endswith(mask_suffixes)]

    counts = {'image': [], 'axon_count': [], 'uaxon_count': []}
    axon_morph_suffix = '_axon_morphometrics.xlsx'
    uaxon_morph_suffix = '_uaxon_morphometrics.xlsx'

    total_axon_count = 0
    total_uaxon_count = 0
    for img in tqdm(inputs):
        if not mask_mode:
            # read morphometric files
            axon_count = len(pd.read_excel(str(img.with_suffix('')) + axon_morph_suffix))
            uaxon_count = len(pd.read_excel(str(img.with_suffix('')) + uaxon_morph_suffix))
        else:
            axonmyelin_mask = str(img.with_suffix('')) + '_seg-axonmyelin-manual.png'
            uaxon_mask = str(img.with_suffix('')) + '_seg-uaxon-manual.png'
            
            axonmyelin = cv2.imread(axonmyelin_mask, cv2.IMREAD_GRAYSCALE) > 200
            uaxon = cv2.imread(uaxon_mask, cv2.IMREAD_GRAYSCALE) > 200

            # count axons
            axon_objects = skm.regionprops(skm.label(axonmyelin))
            uaxon_objects = skm.regionprops(skm.label(uaxon))
            axon_count = len(axon_objects)
            uaxon_count = len(uaxon_objects)

        # add data
        counts['image'].append(img.stem)
        counts['axon_count'].append(axon_count)
        counts['uaxon_count'].append(uaxon_count)
        total_axon_count += axon_count
        total_uaxon_count += uaxon_count

    # save counts
    df = pd.DataFrame(counts)
    df.to_csv(out_name, index=False)
    print(f'Total axon count: {total_axon_count}\nTotal unmyelinated axon count: {total_uaxon_count}')

    
if __name__ == "__main__":
    main()