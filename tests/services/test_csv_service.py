import os
import pytest
from datetime import datetime
from flowpulse.services.CsvService import CsvService
from flowpulse.WorkItem import WorkItem


@pytest.fixture
def test_data_path():
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_data", "testdata.csv")


@pytest.fixture
def csv_service(test_data_path):
    return CsvService(
        file_path=test_data_path,
        delimiter=",",
        started_date_column_name="Started Date",
        closed_date_column_name="Closed Date",
        start_date_format="%Y-%m-%d",
        closed_date_format="%Y-%m-%d",
        estimation_column_name="Story Points",
        item_title_column="Title",
        history_in_days=365,
        today=datetime(2023, 12, 31),
    )


def test_load_items(csv_service):
    items = csv_service.get_items()
    assert len(items) == 6

    # Test complete item
    item1 = items[0]
    assert item1.title == "Task 1"
    assert item1.started_date == datetime(2023, 1, 1)
    assert item1.closed_date == datetime(2023, 1, 10)
    assert item1.estimation == pytest.approx(5.0)

    # Test item with missing closed date
    item3 = items[2]
    assert item3.title == "Task 3"
    assert item3.started_date == datetime(2023, 3, 1)
    assert item3.closed_date == ""
    assert item3.estimation == pytest.approx(8.0)

    # Test item with missing start date
    item4 = items[3]
    assert item4.title == "Task 4"
    assert item4.started_date == ""
    assert item4.closed_date == datetime(2023, 4, 1)
    assert item4.estimation == pytest.approx(2.0)

    # Test item with missing estimation
    item5 = items[4]
    assert item5.title == "Task 5"
    assert item5.estimation == 0

    # Test item with comma in title
    item6 = items[5]
    assert item6.title == "Task with, comma"


def test_write_workitems_to_csv(csv_service, tmp_path):
    # First load some items
    items = csv_service.get_items()

    # Write them to a new CSV
    output_file = "output.csv"
    output_path = os.path.join(tmp_path, output_file)
    CsvService.write_workitems_to_csv(output_path, items)

    # Verify the file exists
    assert os.path.exists(output_path)

    # Create a new service to read the written file
    new_service = CsvService(
        file_path=output_path,
        delimiter=",",
        started_date_column_name="started_date",
        closed_date_column_name="closed_date",
        start_date_format="%Y-%m-%d",
        closed_date_format="%Y-%m-%d",
        estimation_column_name="estimation",
        item_title_column="title",
        history_in_days=365,
        today=datetime(2023, 12, 31),
    )

    # Read items back and verify
    new_items = new_service.get_items()
    assert len(new_items) == len(items)


def test_create_example_file(tmp_path):
    example_file = os.path.join(tmp_path, "example.csv")
    service = CsvService(
        file_path=example_file,
        delimiter=",",
        started_date_column_name="Start",
        closed_date_column_name="End",
        start_date_format="%Y-%m-%d",
        closed_date_format="%Y-%m-%d",
        estimation_column_name="Points",
        item_title_column="Title",
        history_in_days=90,
        today=datetime(2023, 12, 31),
    )

    # Verify example file was created
    assert os.path.exists(example_file)

    # Verify we can read items from it
    items = service.get_items()
    assert len(items) == 100  # Default number of examples
    assert all(isinstance(item, WorkItem) for item in items)
