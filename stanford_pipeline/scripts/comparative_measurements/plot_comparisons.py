'''
This script plots comparisons between manual and automatic measurements of axon 
properties (g-ratio, axon diameter, myelin thickness) for every image in the input 
directory. It also plots global comparisons for metrics aggregated across all images.
'''

from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import argparse


def plot_gratio_comparison(df: pd.DataFrame, title: str, output_path: Path):
    """
    Create a comparison plot between manual and automatic measurements.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the data to plot
    title : str
        Title for the plot
    output_path : Path
        Path where to save the plot
    """
    manual_col = 'gratio'
    auto_col = 'auto_gratio'

    plt.figure(figsize=(18, 6))
    plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-dark.mplstyle')
    
    plt.subplot(1, 2, 1)
    plt.title(title)
    sns.scatterplot(data=df, x=manual_col, y=auto_col)
    plt.plot([0, 1], [0, 1], 'm--')
    plt.xlim(0.4, 1)
    plt.ylim(0.4, 1)    
    plt.xlabel('Manual')
    plt.ylabel('Automatic')
    plt.tight_layout()

    plt.subplot(1, 2, 2)
    plt.title('Difference between manual VS automatic measurements')
    sns.scatterplot(data=df, x=manual_col, y=(df[manual_col] - df[auto_col]))
    plt.axhline(0, color='m', linestyle='--')
    plt.xlabel('Manual measurement')
    plt.ylabel('Manual - Automatic')
    plt.tight_layout()

    plt.savefig(output_path)
    plt.close()


def main(input_dir: str):
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f'Input directory does not exist: {input_path}')
    
    all_data = []
    
    for csv_file in input_path.glob('*_matched_gratios.csv'):
        print(f'Processing {csv_file.name}...')
        df = pd.read_csv(csv_file)
        all_data.append(df)
        
        # Plot g-ratio comparison for current image
        fig_title = f'G-Ratio Comparison for {csv_file.stem}'
        output_path = input_path / f'{csv_file.stem}_comparison_plots.png'
        plot_gratio_comparison(df=df, title=fig_title, output_path=output_path)
    
    # Aggregate data across all images and plot global comparisons
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        fig_title = f'Global g-ratio comparison ({len(combined_df)} measurements)'
        output_path = input_path / 'global_comparison_plots.png'

        plot_gratio_comparison(df=combined_df, title=fig_title, output_path=output_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot comparisons between manual and automatic axon measurements.')
    parser.add_argument(
        '-i', '--input_dir', 
        type=Path, 
        required=True, 
        help='Path to the input directory with CSV files containing matched measurements.'
    )
    args = parser.parse_args()
        
    main(args.input_dir)