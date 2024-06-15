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

        if closed_date:
            self.closed_date = self.parse_jira_date(closed_date)
        
        if started_date:
            self.started_date = self.parse_jira_date(started_date)
        
        if self.started_date and self.closed_date:
            self.cycle_time = (self.closed_date - self.started_date).days + 1
        elif started_date and not self.closed_date:
            self.work_item_age = (datetime.today() - self.started_date).days + 1
            
    def parse_jira_date(self, date):
        # Strip the timezone offset and parse as naive datetime
        date_str = date[:-5]
        date_format = '%Y-%m-%dT%H:%M:%S.%f'
        try:
            return datetime.strptime(date_str, date_format)
        except ValueError as e:
            print(f'Error parsing date {date_str}: {e}')
            return None

    def to_dict(self):
        return {
            'started_date': self.started_date.date(),
            'closed_date': self.closed_date.date(),
            'work_item_age': self.work_item_age,
            'cycle_time': self.cycle_time,
            'closedDate': self.closed_date.date(),
            'state_changed_date': self.started_date.date(),
        }