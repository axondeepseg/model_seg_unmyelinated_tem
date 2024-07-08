'''Reads myelinated + unmyelinated axon morphometric files and count axons.
'''
from pathlib import Path
from tqdm import tqdm
import argparse
import pandas as pd

def main():
    parser = argparse.ArgumentParser(description='Aggregate morphometrics.')
    parser.add_argument('input_dir', type=str, help='Path to the folder containing all morphometric files.')
    parser.add_argument('output_name', type=str, help='Name of the output file.')

    args = parser.parse_args()
    input_dir = Path(args.input_dir)
    out_name = args.output_name
    assert input_dir.exists(), f'Directory {input_dir} does not exist.'

    # find images except for the masks
    mask_suffixes = (
        '_seg-axon.png', '_seg-myelin.png', '_seg-uaxon.png', '_uaxon_index.png', 
        '_seg-axonmyelin.png', '_axonmyelin_index.png', '_index.png',
    )
    inputs = [f for f in input_dir.glob('*.png') if not f.name.endswith(mask_suffixes)]

    counts = {'image': [], 'axon_count': [], 'uaxon_count': []}
    axon_morph_suffix = '_axon_morphometrics.xlsx'
    uaxon_morph_suffix = '_uaxon_morphometrics.xlsx'

    for img in tqdm(inputs):
        # read morphometric files
        axon_count = len(pd.read_excel(str(img.with_suffix('')) + axon_morph_suffix))
        uaxon_count = len(pd.read_excel(str(img.with_suffix('')) + uaxon_morph_suffix))

        # add data
        counts['image'].append(img.stem)
        counts['axon_count'].append(axon_count)
        counts['uaxon_count'].append(uaxon_count)

    # save counts
    df = pd.DataFrame(counts)
    df.to_csv(out_name, index=False)


    
if __name__ == "__main__":
    main()