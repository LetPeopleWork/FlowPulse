from pathlib import Path
import pytest
from PIL import Image
import numpy as np


def compare_images(img1_path: str | Path, img2_path: str | Path) -> bool:
    """
    Compare two images and return True if they are similar enough.

    Args:
        img1_path: Path to first image
        img2_path: Path to second image

    Returns:
        bool: True if images are similar enough, False otherwise
    """
    try:
        test_img = Image.open(img1_path)
        baseline_img = Image.open(img2_path)

        # Convert images to same format and size
        test_img = test_img.convert("RGB").resize((800, 600))
        baseline_img = baseline_img.convert("RGB").resize((800, 600))

        # Compare images with tolerance
        test_array = np.array(test_img)
        baseline_array = np.array(baseline_img)
        difference = np.abs(test_array - baseline_array)

        # Allow for small differences (e.g., due to antialiasing)
        return np.mean(difference) < 5.0

    except Exception as e:
        pytest.fail(f"Image comparison failed: {str(e)}")
