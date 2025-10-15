'''
This utility takes as input the coordinates of each individual axon manually 
measured by an expert in ImageJ. The actual coordinates represent a point within 
the myelin of each axon. The script then finds the corresponding axon in the 
segmented image and assigns the axon ID to the object. Also writes the 
automatically computed g-ratio/axon_diam/myelin_thickness to the output file, 
which will allow us to compare manual and automatic measurements.

Warnings
--------
- If the coordinates are not segmented as myelin, no axon ID will be assigned. 
- If multiple coordinates map to the same axon, this axon ID is removed.

We assume the following input structure:

csv_dir/
├─ img1.png
├─ img1_manual_gratios.csv          <-- important: contains manual measurements (for N axons in the image)
├─ ...
segmented_dir/
├─ img1.png
├─ img1_seg-axon.png
├─ img1_seg-myelin.png
├─ img1_seg-uaxon.png
├─ img1_axon_morphometrics.xlsx     <-- important: contains auto measurements (for ~all M axons in the image with M >> N)
├─ img1_instance_map.png            <-- important: 16-bit instance seg
├─ ...

'''


from pathlib import Path
import imageio
import pandas as pd
import argparse
import matplotlib.pyplot as plt


def verify_inputs(csv_path: Path, morpho_path: Path, instance_map_path: Path):
    if not csv_path.exists():
        raise FileNotFoundError(f'Missing CSV file: {csv_path}')
    if not morpho_path.exists():
        raise FileNotFoundError(f'Missing morphometrics file: {morpho_path}')
    if not instance_map_path.exists():
        raise FileNotFoundError(f'Missing instance map image: {instance_map_path}')


def main(csv_dir: Path, segmented_dir: Path):
    img_list = sorted(csv_dir.glob('*resized.png'))
    
    for img_path in img_list:
        stem = img_path.stem
        print(f'Processing {stem}...')
        
        csv_path = csv_dir / f'{stem}_manual_gratios.csv'
        morpho_path = segmented_dir / f'{stem}_axon_morphometrics.xlsx'
        instance_map_path = segmented_dir / f'{stem}_instance-map.png'
        
        verify_inputs(csv_dir, segmented_dir, instance_map_path)
        
        # read input files
        df_manual = pd.read_csv(csv_path)
        df_auto = pd.read_excel(morpho_path)
        instance_map = imageio.imread(instance_map_path)

        output_df = df_manual.copy()
        output_df['axon_id'] = None
        output_df['auto_g-ratio'] = None
        output_df['auto_axon_diam'] = None
        output_df['auto_myelin_thickness'] = None

        axon_ids = []
        # look at all the axons my friend
        for idx, row in df_manual.iterrows():
            x, y = int(row['x_new']), int(row['y_new'])
            axon_id = instance_map[x, y] - 1
            if axon_id < 0:
                print(f'Warning: Coordinate ({x}, {y}) not in myelin. Skipping.')
                continue
            axon_ids.append(axon_id)

            auto_row = df_auto.loc[axon_id]

            output_df.at[idx, 'axon_id'] = axon_id
            output_df.at[idx, 'auto_g-ratio'] = auto_row['gratio']
            output_df.at[idx, 'auto_axon_diam'] = auto_row['axon_diam (um)']
            output_df.at[idx, 'auto_myelin_thickness'] = auto_row['myelin_thickness (um)']

        # check for duplicates
        if len(set(axon_ids)) < len(axon_ids):
            print('If you read this, go fix duplicates.')

        output_path = csv_dir / f'{stem}_matched_gratios.csv'
        output_df.to_csv(output_path, index=False)
    

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Match manually measured axon coordinates to segmented axons.')
    ap.add_argument('csv_dir', type=Path, help='Directory containing CSV file for every image.')
    ap.add_argument('segmented_dir', type=Path, help='Directory containing segmented images.')
    args = ap.parse_args().csv_dir, ap.parse_args().segmented_dir
    csv_dir, segmented_dir = args
    main(Path(csv_dir), Path(segmented_dir))