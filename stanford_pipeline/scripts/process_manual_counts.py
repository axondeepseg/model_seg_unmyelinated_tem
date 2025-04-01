'''
This script is used to compare the counts of segmented axons (myelinated and 
unmyelinated) against a manual count (taken from an array of positions recorded 
in Fiji).
'''
import argparse
from pathlib import Path
import pandas as pd

# the following areas are in microns^2 and only consider the ROIs where 
# manual counts were taken
TOTAL_AREA_PER_SUBJECT = {
    "366A": 0.00493**2 * 41719555,
    "367A": 0.00493**2 * 51328512,
    "368A": 0.00493**2 * 32035639,
    "369B": 0.00493**2 * 100842822,
    "370":  0.00493**2 * (42637356 + 55058165),
    "371":  0.00493**2 * (25254350 + 21779850),
    "372":  0.00493**2 * (20519956 + 21142618),
    "373C": 0.00493**2 * (19282050 + 20393350),
    "374":  0.00493**2 * (37205539 + 11425762),
    "375":  0.00493**2 * (32541350 + 12116886)
}


def main(input_dir):

    counts = pd.DataFrame(columns=['image', 'subject', 'axon_count', 'uaxon_count'])

    for p in Path(input_dir).glob('*.csv'):
        subject = p.name.split('_')[0]
        df = pd.read_csv(str(p))
        n1 = len(df[df['Counter'] == 1])
        n2 = len(df[df['Counter'] == 2])

        new_col = {
            'image': str(p.name),
            'subject': subject,
            'axon_count': n2,
            'uaxon_count': n1
        }
        counts = pd.concat([counts, pd.DataFrame(new_col, index=[0])], ignore_index=True)
    
    counts['percent'] = 100 * counts['axon_count'] / (counts['axon_count'] + counts['uaxon_count'])

    # sum counts by subject
    counts_sum = counts.drop(columns=['image', 'uaxon_count']).groupby('subject').agg({'axon_count': 'sum'}).reset_index()
    # add total area per subject to the dataframe
    counts_sum['total_area'] = counts_sum['subject'].map(TOTAL_AREA_PER_SUBJECT)
    counts_sum['density'] = counts_sum['axon_count'] / counts_sum['total_area']
    print('\n\tDENSITY')
    print(counts_sum)

    # average percent per suject
    percent = counts.drop(columns=['image', 'axon_count', 'uaxon_count']).groupby('subject').agg({'percent': 'mean'}).reset_index()
    print('\n\t% MYELINATED [mean value per subject]')
    print(percent)

    # alternative way to calculte percentages
    percent_alt = counts.drop(columns=['image', 'percent']).groupby('subject').agg({'axon_count': 'sum', 'uaxon_count': 'sum'}).reset_index()
    percent_alt['percent'] = 100 * percent_alt['axon_count'] / (percent_alt['axon_count'] + percent_alt['uaxon_count'])
    print('\n\t% MYELINATED [sum per subject]')
    print(percent_alt)
    

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input_dir', type=str, help='Path to the folder containing manual counts (CSVs).')
    args = ap.parse_args()

    main(args.input_dir)