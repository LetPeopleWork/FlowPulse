from datetime import timedelta


class WorkItemFilterService:

    def __init__(self, today, history_days):
        self.today = today
        self.history_days = history_days

    def get_closed_items(self, work_items):
        start_date = self.today - timedelta(days=self.history_days)
        return [
            item
            for item in work_items
            if item.closed_date and start_date <= item.closed_date <= self.today
        ]

    def get_open_items(self, work_items):
        return [item for item in work_items if item.was_active_on(self.today.date())]

    def get_in_progress_items(self, work_items):
        start_date = self.today - timedelta(days=self.history_days)

        return [
            item
            for item in work_items
            if item.started_date
            and item.started_date <= self.today
            and (
                not item.closed_date
                or (item.closed_date > start_date and item.closed_date <= self.today)
            )
        ]

    def get_items_opened_in_period(self, work_items):
        start_date = self.today - timedelta(days=self.history_days)

        return [
            item
            for item in work_items
            if item.started_date
            and item.started_date <= self.today
            and item.started_date >= start_date
        ]
