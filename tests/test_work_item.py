import unittest
from datetime import datetime, date
from flowpulse.WorkItem import WorkItem


class TestWorkItem(unittest.TestCase):
    def setUp(self):
        self.today = date(2023, 12, 1)
        self.started_date = datetime(2023, 11, 1)
        self.closed_date = datetime(2023, 11, 15)

    def test_initialization(self):
        work_item = WorkItem("123", "Test Item", self.started_date, self.closed_date, 5)
        self.assertEqual(work_item.id, "123")
        self.assertEqual(work_item.title, "Test Item")
        self.assertEqual(work_item.cycle_time, 15)
        self.assertEqual(work_item.estimation, 5)

    def test_active_work_item(self):
        work_item = WorkItem("123", "Test Item", self.started_date, None, 5)
        self.assertIsNone(work_item.cycle_time)
        self.assertIsNotNone(work_item.work_item_age)

    def test_was_active_on(self):
        work_item = WorkItem("123", "Test Item", self.started_date, self.closed_date, 5)
        self.assertTrue(work_item.was_active_on(date(2023, 11, 5)))
        self.assertFalse(work_item.was_active_on(date(2023, 10, 31)))
        self.assertFalse(work_item.was_active_on(date(2023, 11, 16)))

    def test_get_work_item_age(self):
        work_item = WorkItem("123", "Test Item", self.started_date, self.closed_date, 5)
        self.assertEqual(work_item.get_work_item_age(date(2023, 11, 5)), 5)
        self.assertIsNone(work_item.get_work_item_age(date(2023, 10, 31)))

    def test_to_dict(self):
        work_item = WorkItem("123", "Test Item", self.started_date, self.closed_date, 5)
        result = work_item.to_dict()
        self.assertEqual(result["started_date"], self.started_date.date())
        self.assertEqual(result["closed_date"], self.closed_date.date())
        self.assertEqual(result["cycle_time"], 15)


if __name__ == "__main__":
    unittest.main()
