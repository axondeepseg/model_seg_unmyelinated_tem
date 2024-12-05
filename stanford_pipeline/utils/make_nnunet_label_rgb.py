import cv2
from pathlib import Path
import argparse

CLASSES = {
    1: "uaxon",
    2: "myelin",
    3: "axon",
    4: "nuclei",
    5: "process",
}

MAPPING = {
    "uaxon": (250, 242, 235),
    "myelin": (54, 148, 103),
    "axon": (0, 190, 165), 
    "nuclei": (141, 102, 5),  
    "process": (161, 122, 66),
}

def main(target_path):
    fnames = [str(f) for f in target_path.glob("*.png")]
    for fname in fnames:
        im = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
        # transform into rgb
        im_rgb = cv2.cvtColor(im, cv2.COLOR_GRAY2RGB)
        for k, cl in CLASSES.items():
            color = MAPPING[cl]
            im_rgb[im == k] = color
        cv2.imwrite(fname.replace(".png", "_rgb.png"), im_rgb)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-t", "--target_path", required=True, help="Path to the target folder containing the png files.")
    args = ap.parse_args()
    
    main(Path(args.target_path))