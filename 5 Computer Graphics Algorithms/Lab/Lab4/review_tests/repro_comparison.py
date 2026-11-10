"""Read-only reproduction of the missing-original-Lab3 comparison."""
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
LAB4 = HERE.parent
sys.path.insert(0, str(LAB4))
import numpy as np
from PIL import Image
from lab4_spectrum.experiment import run, white_scene


def main():
    data = run(white_scene())
    records = []
    for index, image in enumerate(data["images"][1:], 1):
        original_path = LAB4.parent / "Lab3" / "lab3_color_sphere" / "results" / "white" / f"image_{index}.png"
        original = np.asarray(Image.open(original_path).convert("RGB"))
        records.append({
            "image": index,
            "lab4_shape": list(image.shape),
            "lab3_shape": list(original.shape),
            "lab4_max_channel_spread": int(np.ptp(image.astype(int), axis=-1).max()),
            "lab3_max_channel_spread": int(np.ptp(original.astype(int), axis=-1).max()),
            "uses_original_lab3_pixels": bool(np.array_equal(image, original)),
        })
    print(json.dumps(records, ensure_ascii=False, indent=2))
    assert all(r["uses_original_lab3_pixels"] for r in records), "GUI comparison images are recomputed, not original Lab3 image_1/image_2"


if __name__ == "__main__":
    main()
