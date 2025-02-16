import pytest
from pathlib import Path
from PIL import Image
import numpy as np

# Mark entire module as integration tests
pytestmark = pytest.mark.integration


def images_match(img1_path: str, img2_path: str, threshold: float = 0.01) -> bool:
    """Compare two images and return True if they are similar enough"""
    img1 = np.array(Image.open(img1_path))
    img2 = np.array(Image.open(img2_path))

    if img1.shape != img2.shape:
        return False

    diff = np.abs(img1 - img2).mean()
    max_val = 255

    return (diff / max_val) < threshold


def test_generated_charts_match_baseline():
    """Test that all generated charts match their baseline versions"""
    # List of expected charts from config
    expected_charts = [
        "test_cycle_time_scatter.png",
        "test_work_item_age.png",
        "test_throughput.png",
        "test_wip.png",
        "test_started_vs_finished.png",
        "test_estimation_vs_cycle_time.png",
        "test_pbc_throughput.png",
        "test_pbc_cycle_time.png",
        "test_pbc_wip.png",
        "test_pbc_total_age.png",
    ]

    # Check each generated chart against baseline
    for chart_name in expected_charts:
        generated_path = Path("../test_charts") / chart_name
        baseline_path = Path("baseline_charts") / chart_name

        assert generated_path.exists(), f"Generated chart {chart_name} not found"
        assert baseline_path.exists(), f"Baseline chart {chart_name} not found"
        assert images_match(
            str(generated_path), str(baseline_path)
        ), f"Generated chart {chart_name} differs from baseline"
