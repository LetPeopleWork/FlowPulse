import os
from ..WorkItem import WorkItem
from datetime import datetime, timedelta

import random

import csv


class CsvService:

    def __init__(
        self,
        file_path,
        delimiter,
        started_date_column_name,
        closed_date_column_name,
        start_date_format,
        closed_date_format,
        estimation_column_name,
        item_title_column,
        history_in_days,
        today,
    ):
        self.file_path = file_path
        self.delimiter = delimiter
        self.started_date_column_name = started_date_column_name
        self.closed_date_column_name = closed_date_column_name
        self.start_date_format = start_date_format
        self.closed_date_format = closed_date_format if closed_date_format else start_date_format
        self.estimation_column_name = estimation_column_name
        self.item_title_column = item_title_column
        self.today = today
        self.history_in_days = history_in_days

        print("Using following CSV file: {0}".format(self.file_path))
        if not os.path.isfile(file_path):
            print("File does not exist. Creating example file")
            self.write_example_file()

    def get_items(self, items_query=None):
        print(
            (
                "Loading Items from CSV File: '{0}'. "
                "Started Date Column Name '{1}', "
                "Closed Date Column Name '{2}', "
                "Start Date Format '{3}', "
                "and Closed Date Format '{4}'"
            ).format(
                self.file_path,
                self.started_date_column_name,
                self.closed_date_column_name,
                self.start_date_format,
                self.closed_date_format,
            )
        )
        work_items = []

        encodings = ["utf-8-sig", "utf-8", "latin-1", "cp1252"]
        for encoding in encodings:
            try:
                with open(self.file_path, "r", encoding=encoding) as file:
                    csv_reader = csv.DictReader(file, delimiter=self.delimiter)

                    for row in csv_reader:
                        closed_date = row[self.closed_date_column_name]
                        if closed_date:
                            closed_date = datetime.strptime(closed_date, self.closed_date_format)

                        started_date = row[self.started_date_column_name]
                        if started_date:
                            started_date = datetime.strptime(started_date, self.start_date_format)

                        estimation = None
                        if self.estimation_column_name in row:
                            raw_estimate = row[self.estimation_column_name]
                            estimation = 0

                            if raw_estimate:
                                estimation = float(row[self.estimation_column_name])

                        item_title = ""
                        if self.item_title_column in row:
                            item_title = row[self.item_title_column]

                        work_items.append(
                            WorkItem(item_title, item_title, started_date, closed_date, estimation)
                        )

                    # If we successfully read the file, break the loop
                    break
            except UnicodeDecodeError:
                # If this encoding didn't work, try the next one
                continue

            if not work_items:
                raise ValueError(
                    f"Could not read the CSV file with any of the following encodings: {encodings}"
                )

        if items_query:
            print("Items Query not supported for CSV - Loading all items that are NOT closed")
            work_items = [item for item in work_items if not item.closed_date]

        print("Found {0} Items in the CSV".format(len(work_items)))

        return work_items

    @staticmethod
    def write_workitems_to_csv(csv_file_path, work_items):
        if csv_file_path:
            with open(csv_file_path, mode="w", newline="") as csv_file:
                writer = csv.writer(csv_file)

                writer.writerow(
                    [
                        "id",
                        "title",
                        "estimation",
                        "started_date",
                        "closed_date",
                        "work_item_age",
                        "cycle_time",
                        "state_changed_date",
                    ]
                )

                for item in work_items:
                    row = [
                        str(item.id),
                        str(item.title),
                        str(item.estimation),
                        item.started_date.date().isoformat() if item.started_date else "",
                        item.closed_date.date().isoformat() if item.closed_date else "",
                        str(item.work_item_age) if item.work_item_age is not None else "",
                        str(item.cycle_time) if item.cycle_time is not None else "",
                        item.started_date.date().isoformat() if item.started_date else "",
                    ]

                    writer.writerow(row)

            print(f"Work items exported to {csv_file_path}")

    def write_example_file(self):
        print("Writing Example File with random values to {0}".format(self.file_path))

        with open(self.file_path, "w", newline="") as file:
            writer = csv.writer(file, delimiter=self.delimiter)
            field = [
                self.started_date_column_name,
                self.closed_date_column_name,
                self.estimation_column_name,
                self.item_title_column,
            ]

            # Write Header
            writer.writerow(field)

            story_points = [1, 2, 3, 5, 8, 13]

            # Generate and write 100 random dates
            for index in range(100):
                start_date_delta = random.randint(10, self.history_in_days + 10)
                end_date_delta = random.randint(-10, self.history_in_days)

                random_start_date = self.today - timedelta(days=start_date_delta)
                random_end_date = self.today - timedelta(days=end_date_delta)

                started_date = random_start_date.strftime(self.start_date_format)
                end_date = ""

                if end_date_delta <= start_date_delta:
                    end_date = random_end_date.strftime(self.closed_date_format)

                estimation = random.choice(story_points)

                writer.writerow([started_date, end_date, estimation, index])
