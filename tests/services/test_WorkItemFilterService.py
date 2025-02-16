import pytest
from datetime import datetime, timedelta
from flowpulse.WorkItem import WorkItem
from flowpulse.services.WorkItemFilterService import WorkItemFilterService


class TestWorkItemFilterService:
    @pytest.fixture
    def today(self):
        return datetime(2023, 1, 15)

    @pytest.fixture
    def filter_service(self, today):
        return WorkItemFilterService(today, 30)

    @pytest.fixture
    def work_items(self, today):
        return [
            # Started Within Period, Closed item within Period
            WorkItem("1", "Item 1", today - timedelta(days=20), today - timedelta(days=10), 5),
            # Open item started before period, not closed
            WorkItem("2", "Item 2", today - timedelta(days=40), None, 3),
            # Started and Closed item before period
            WorkItem("3", "Item 3", today - timedelta(days=40), today - timedelta(days=35), 8),
            # In progress item started within period
            WorkItem("4", "Item 4", today - timedelta(days=15), None, 5),
            # Future item
            WorkItem("5", "Item 5", today + timedelta(days=5), None, 3),
        ]

    def test_get_closed_items(self, filter_service, work_items):
        closed_items = filter_service.get_closed_items(work_items)
        assert len(closed_items) == 1
        assert closed_items[0].id == "1"

    def test_get_open_items(self, filter_service, work_items):
        open_items = filter_service.get_open_items(work_items)
        assert len(open_items) == 2
        assert {item.id for item in open_items} == {"2", "4"}

    def test_get_in_progress_items(self, filter_service, work_items):
        in_progress_items = filter_service.get_in_progress_items(work_items)
        assert len(in_progress_items) == 3
        assert {item.id for item in in_progress_items} == {"1", "2", "4"}

    def test_get_items_opened_in_period(self, filter_service, work_items):
        opened_items = filter_service.get_items_opened_in_period(work_items)
        assert len(opened_items) == 2
        assert {item.id for item in opened_items} == {"1", "4"}

    def test_empty_work_items(self, filter_service):
        empty_items = []
        assert filter_service.get_closed_items(empty_items) == []
        assert filter_service.get_open_items(empty_items) == []
        assert filter_service.get_in_progress_items(empty_items) == []
        assert filter_service.get_items_opened_in_period(empty_items) == []

    def test_different_history_period(self, today):
        short_period_service = WorkItemFilterService(today, 10)
        long_period_service = WorkItemFilterService(today, 60)

        items = [
            WorkItem("1", "Item 1", today - timedelta(days=20), today - timedelta(days=15), 5),
        ]

        assert len(short_period_service.get_closed_items(items)) == 0
        assert len(long_period_service.get_closed_items(items)) == 1

    def test_edge_case_dates(self, today):
        service = WorkItemFilterService(today, 30)
        edge_items = [
            # Item closed exactly 30 days ago
            WorkItem("1", "Edge 1", today - timedelta(days=35), today - timedelta(days=30), 5),
            # Item started exactly today
            WorkItem("2", "Edge 2", today, None, 3),
        ]

        closed_items = service.get_closed_items(edge_items)
        open_items = service.get_open_items(edge_items)

        assert len(closed_items) == 1
        assert len(open_items) == 1
