from pathlib import Path
import pytest
import os
import json
from tests.utils.test_utils import compare_images

# Mark entire module as integration tests
pytestmark = pytest.mark.integration


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
        generated_path = Path(os.path.join("tests", "test_charts", chart_name))
        baseline_path = Path(os.path.join("tests", "baseline_charts", chart_name))

        assert generated_path.exists(), f"Generated chart {chart_name} not found"
        assert baseline_path.exists(), f"Baseline chart {chart_name} not found"
        assert compare_images(
            generated_path, baseline_path
        ), f"Generated chart {chart_name} differs from baseline"


def test_raw_data_csv_generation():
    """Test that the rawDataCSV file is properly generated as specified in the config."""
    # Load the config file to get the rawDataCSV filename
    config_path = Path(os.path.join("tests", "integration", "IntegrationTestConfig.json"))
    assert config_path.exists(), "Integration test config not found"

    with open(config_path, "r") as f:
        config = json.load(f)

    raw_data_csv_filename = config["general"]["rawDataCSV"]
    charts_folder = config["general"]["chartsFolder"].replace("../", "")

    # Check if the CSV file exists in the charts folder
    csv_path = Path(os.path.join("tests", charts_folder, raw_data_csv_filename))
    assert (
        csv_path.exists()
    ), f"Raw data CSV file '{raw_data_csv_filename}' not found in {charts_folder}"

    # Check that the file has content (not empty)
    file_size = csv_path.stat().st_size
    assert file_size > 0, f"Raw data CSV file '{raw_data_csv_filename}' exists but is empty"
