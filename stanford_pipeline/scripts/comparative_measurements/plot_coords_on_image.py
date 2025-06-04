"""
Script to plot coordinate points from a CSV file onto an image.

This script takes an image file and a corresponding CSV file containing
coordinates, then overlays the points on the image for visualization.
"""
import sys
import argparse
from pathlib import Path
import pandas as pd
from PIL import Image, ImageDraw

__author__ = "Armand Collin"


def load_coords(csv_path: Path) -> list:
    """
    Load coordinates from a CSV file.

    Args:
        csv_path (Path): Path to the CSV file containing coordinates.

    Returns:
        list: List of tuples containing coordinates (x, y).
    """
    coords = []
    try:
        df = pd.read_csv(csv_path, sep=',')
        coords = df[['x_new', 'y_new']].astype(int).values.tolist()
        
        return coords
    except Exception as e:
        print(f"Error loading coordinates from {csv_path}: {e}", file=sys.stderr)

def overlay_coordinates_on_image(image_path: Path, coords: list):
    """
    Overlay coordinates on an image.

    Args:
        image_path (Path): Path to the input image file.
        coords (list): List of tuples containing coordinates (x, y).
    """
    try:
        image = Image.open(image_path).convert("RGB")
        # fill with black
        image = Image.new("RGB", image.size, (0, 0, 0))
        draw = ImageDraw.Draw(image)

        for y, x in coords:
            colo = 'red'
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=colo, outline=colo)

        output_path = image_path.with_name(f"{image_path.stem}_coords.png")
        image.save(output_path)
        print(f"Coordinates overlay saved to {output_path}")
    except Exception as e:
        print(f"Error overlaying coordinates on image: {e}", file=sys.stderr)
    

def main():
    """Main function to plot coordinates on an image."""
    parser = argparse.ArgumentParser(
        description="Plot coordinate points from CSV onto an image"
    )
    parser.add_argument(
        "image_path",
        type=Path,
        help="Path to the input image file"
    )
    
    args = parser.parse_args()
    csv_fname = args.image_path.name.replace('.png', '_manual_gratios.csv')
    csv_path = args.image_path.parent / csv_fname
    
    # Validate input files exist
    if not args.image_path.exists():
        print(f"Error: Image file '{args.image_path}' not found", file=sys.stderr)
        return 1
    
    if not csv_path.exists():
        print(f"Error: CSV file '{csv_path}' not found", file=sys.stderr)
        return 1
    
    print(f"Processing image: {args.image_path}")
    coords = load_coords(csv_path)
    print(f"Using {len(coords)} coordinates from: {csv_path}")

    overlay_coordinates_on_image(args.image_path, coords)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())