"""Prepare and classify a single external image of a handwritten digit."""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

from network import load_model, softmax


DEFAULT_MODEL = Path(__file__).resolve().parents[1] / "models" / "best_model.npz"


def _grayscale(path):
    with Image.open(path) as original:
        image = ImageOps.exif_transpose(original).convert("RGBA")

    alpha = np.asarray(image.getchannel("A"))
    gray = image.convert("L")
    if np.all(alpha == 255):
        return np.asarray(gray, dtype=np.float32)

    visible = alpha > 0
    if not visible.any():
        raise ValueError("The image is fully transparent.")

    # Give transparent sketches a background that contrasts with the stroke.
    background = 0 if np.median(np.asarray(gray)[visible]) > 127 else 255
    gray = Image.composite(gray, Image.new("L", gray.size, background), image.getchannel("A"))
    return np.asarray(gray, dtype=np.float32)


def preprocess_image(path):
    """Return a normalized 28 × 28 image with a bright digit on a dark background."""
    gray = _grayscale(path)
    border = np.concatenate((gray[0], gray[-1], gray[1:-1, 0], gray[1:-1, -1]))
    background = np.median(border)
    if background - gray.min() > gray.max() - background:
        gray = 255 - gray
        background = 255 - background

    foreground = np.maximum(gray - background, 0)
    peak = foreground.max()
    if peak < 8:
        raise ValueError("No digit with sufficient contrast was found.")

    # Use the mask for the bounding box, keeping antialiasing inside it.
    rows, cols = np.nonzero(foreground >= max(8, 0.10 * peak))
    cropped = foreground[rows.min() : rows.max() + 1, cols.min() : cols.max() + 1]
    height, width = cropped.shape
    scale = 20 / max(height, width)
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    digit = Image.fromarray(cropped.astype(np.uint8)).resize(size, Image.Resampling.LANCZOS)

    canvas = Image.new("L", (28, 28))
    canvas.paste(digit, ((28 - size[0]) // 2, (28 - size[1]) // 2))
    pixels = np.asarray(canvas, dtype=np.float32)
    mass = pixels.sum()
    if mass == 0:
        raise ValueError("The digit disappeared during resizing.")

    coordinates = np.arange(28)
    center_x = pixels.sum(axis=0) @ coordinates / mass
    center_y = pixels.sum(axis=1) @ coordinates / mass
    # Pillow's affine transform maps each output coordinate back to the input.
    centered = canvas.transform(
        (28, 28),
        Image.Transform.AFFINE,
        (1, 0, center_x - 13.5, 0, 1, center_y - 13.5),
        resample=Image.Resampling.BILINEAR,
    )
    return np.asarray(centered, dtype=np.float32) / 255.0


def predict_image(model, path):
    """Return the predicted digit and probabilities in class order 0 through 9."""
    image = preprocess_image(path)
    probabilities = softmax(model.forward(image[None, ...]))[0]
    return int(probabilities.argmax()), probabilities


def main():
    parser = argparse.ArgumentParser(description="Classify a drawing with the saved MNIST model.")
    parser.add_argument("image", type=Path)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    args = parser.parse_args()
    prediction, probabilities = predict_image(load_model(args.model), args.image)
    print(f"Prediction: {prediction}")
    for digit, probability in enumerate(probabilities):
        print(f"{digit}: {probability:.6f}")


if __name__ == "__main__":
    main()
