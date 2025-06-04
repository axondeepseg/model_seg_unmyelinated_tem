import pandas as pd
import numpy as np
from pathlib import Path

__author__ = "Armand Collin"


def preprocess_manual_measurements(file_path: Path) -> pd.DataFrame:
    """
    Preprocess manual measurements from a CSV file.

    Args:
        file_path (Path): Path to the CSV file containing manual measurements.

    Returns:
        pd.DataFrame: Preprocessed DataFrame with relevant columns.
    """
    df = pd.read_csv(file_path, sep=',', header=None)
    df.columns = ['fname_and_coords', 'myelin_thickness', 'axon_diam', 'gratio']

    # split filename and coords
    df[['fname', 'coords']] = df['fname_and_coords'].str.split(':', n=1, expand=True)
    # sanitize filenames
    df['fname'] = df['fname'].str.replace(' ', '_', regex=False)
    df['fname'] = df['fname'].str.replace('#', '-', regex=False)

    # split coords string
    df[['x', 'y']] = df['coords'].str.split('-', n=1, expand=True)
    # check if all x-y coords are numeric
    if not df['x'].str.isnumeric().all() or not df['y'].str.isnumeric().all():
        raise ValueError("Non-numeric values found in x or y coordinates.")
    mask_valid_coords = df['x'].notna() & df['y'].notna()
    if not mask_valid_coords.all():
        # print invalid coords
        invalid_coords = df[~mask_valid_coords]
        print("Invalid coordinates found:")
        print(invalid_coords[['fname', 'x', 'y']])
        # remove invalid rows
        df = df[mask_valid_coords]
        
    df['x'] = df['x'].astype(int)
    df['y'] = df['y'].astype(int)
    # # our target images are 4x smaller than the original images
    df['x_new'] = df['x'] // 4
    df['y_new'] = df['y'] // 4

    return df

def main():
    file_path = Path('all_manual_gratios.csv')
    preprocessed_df = preprocess_manual_measurements(file_path)
    print(preprocessed_df)

    # save a new CSV for every unique filename
    for fname, group in preprocessed_df.groupby('fname'):
        fname_no_ext = fname.replace('.tif', '_8bit_eq_resized').replace('Stitched', 'stitched')
        output_file = Path(f"{fname_no_ext}_manual_gratios.csv")
        group.to_csv(output_file, index=False)
        print(f"Saved preprocessed data for {fname} to {output_file}")

if __name__ == "__main__":
    main()