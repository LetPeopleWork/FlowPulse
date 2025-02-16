from datetime import datetime


class WorkItem:
    def __init__(self, id, title, started_date, closed_date, estimation):
        self.id = id
        self.started_date = None
        self.closed_date = None
        self.title = title
        self.estimation = estimation

        self.item_title = id

        self.work_item_age = None
        self.cycle_time = None
        self.closed_date = closed_date
        self.started_date = started_date

        if self.started_date and self.closed_date:
            self.cycle_time = (self.closed_date - self.started_date).days + 1
        elif started_date and not self.closed_date:
            self.work_item_age = (datetime.today() - self.started_date).days + 1

    def was_active_on(self, date):
        if not self.started_date:
            return False

        if self.started_date.date() > date:
            return False

        if not self.closed_date:
            return True

        return self.closed_date.date() >= date

    def get_work_item_age(self, date):
        if not self.was_active_on(date):
            return None

        return (date - self.started_date.date()).days + 1

    def to_dict(self):
        result = {
            "work_item_age": self.work_item_age,
            "cycle_time": self.cycle_time,
        }
        if self.started_date:
            result["started_date"] = self.started_date.date()
        if self.closed_date:
            result["closed_date"] = self.closed_date.date()
        return result
