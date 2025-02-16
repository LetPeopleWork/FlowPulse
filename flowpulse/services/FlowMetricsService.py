from datetime import datetime, timedelta

from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import adjustText as adjustText

import numpy as np
import pandas as pd

from collections import Counter

import os


class FlowMetricsService:

    def __init__(
        self,
        show_plots,
        charts_folder,
        work_item_filter_service,
        history,
        plot_labels=True,
        today=datetime.today(),
    ):
        self.show_plots = show_plots
        self.charts_folder = charts_folder
        self.today = today
        self.plot_labels = plot_labels
        self.history = history
        self.work_item_filter_service = work_item_filter_service

        self.current_date = datetime.now().strftime("%d.%m.%Y")

        if not os.path.exists(charts_folder):
            os.makedirs(charts_folder)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(script_dir, "logo.png")
        self.logo = mpimg.imread(logo_path)

    def plot_cycle_time_scatterplot(
        self, items, percentiles, percentile_colors, chart_name, trend_settings=None
    ):
        print(
            "Creating Cycle Time Scatterplot with following config: "
            "Chart Name: {0}, Percentiles: {1}, "
            "Percentile Colors: {2}, Trend Settings: {3}".format(
                chart_name, percentiles, percentile_colors, trend_settings
            )
        )

        # Get only items that were closed within the specified history
        items = self.work_item_filter_service.get_closed_items(items)

        cycle_times = [item.cycle_time for item in items if item.cycle_time is not None]

        if not cycle_times:
            print("No closed work items for plotting.")
            return

        items = [item for item in items if item.closed_date and item.started_date]
        cycle_times = [item.cycle_time for item in items if item.cycle_time is not None]
        dates = [item.closed_date.date() for item in items]

        if not cycle_times:
            print("No closed work items within the specified history for plotting.")
            return

        plt.figure(figsize=(15, 9))
        plt.scatter(dates, cycle_times)

        if self.plot_labels:
            texts = []
            if self.plot_labels:
                for item in items:
                    text = plt.text(
                        item.closed_date.date(), item.cycle_time, item.item_title, ha="center"
                    )
                    texts.append(text)

            # Adjust text to avoid overlap
            adjustText.adjust_text(texts, arrowprops=dict(arrowstyle="-", color="k", lw=0.5))

        plt.title("Cycle Time Scatterplot")
        plt.xlabel("Work Item Closed Date")
        plt.ylabel("Cycle Time (days)")
        plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.gca().set_ylim(bottom=0)

        self.add_timestamp(plt)

        # Calculate percentiles
        percentile_values = np.percentile(cycle_times, percentiles)

        # Plot percentile lines
        for value, label, color in zip(percentile_values, percentiles, percentile_colors):
            plt.axhline(
                y=value,
                color=color,
                linestyle="--",
                label=f"{label}th Percentile ({int(value)} Days)",
            )

        # Calculate the rolling percentile for the specified window size

        if trend_settings:
            trend_window_size = trend_settings[1]
            trend_percentile = trend_settings[0]
            trend_color = trend_settings[2]

            if len(dates) >= trend_window_size:
                df = pd.DataFrame({"date": dates, "cycle_time": cycle_times})
                df = df.sort_values("date")
                rolling_percentile_values = (
                    df["cycle_time"]
                    .rolling(window=trend_window_size)
                    .apply(lambda x: np.percentile(x, trend_percentile), raw=True)
                )
                plt.plot(
                    df["date"],
                    rolling_percentile_values,
                    label=f"{trend_window_size}-day Trend ({trend_percentile}th Percentile)",
                    color=trend_color,
                    linestyle="dotted",
                )

        plt.legend()

        self.add_logo(plt)

        chart_file_path = os.path.join(self.charts_folder, chart_name)
        print("Storing file at {0}".format(chart_file_path))
        plt.savefig(chart_file_path)

        if self.show_plots:
            plt.show()

    def plot_work_item_age_scatterplot(self, items, x_axis_lines, x_axis_line_colors, chart_name):
        print(
            "Creating Work Item Scatterplot with following config: "
            "Chart Name: {0}, X-Axis Lines: {1}, X-Axis Line Colors: {2}".format(
                chart_name, x_axis_lines, x_axis_line_colors
            )
        )

        # Get only items that were closed within the specified history
        filtered_items = self.work_item_filter_service.get_open_items(items)

        work_item_ages = [item.get_work_item_age(self.today.date()) for item in filtered_items]
        if not work_item_ages:
            print("No work items with age for plotting.")
            return

        # Set default size to be wider (10 inches width and 6 inches height in this example)
        plt.figure(figsize=(15, 9))

        dates = [item.started_date.date() for item in filtered_items]

        # Plot Work Item Age as triangles
        plt.scatter(dates, work_item_ages, label="Work Item Age (days)", alpha=0.7)

        if self.plot_labels:
            texts = []
            for item in filtered_items:
                work_item_age = item.get_work_item_age(self.today.date())

                if work_item_age:
                    text = plt.text(
                        item.started_date.date(), work_item_age, item.item_title, ha="center"
                    )
                    texts.append(text)

            # Adjust text to avoid overlap
            adjustText.adjust_text(texts, arrowprops=dict(arrowstyle="-", color="k", lw=0.5))

        plt.title("Work Item Age Scatterplot with Cycle Time Percentiles")
        plt.xlabel("Work Item Started Date")
        plt.ylabel("Time (days)")
        plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
        plt.gca().set_ylim(bottom=0)

        self.add_timestamp(plt)

        # Get Closed Items
        closed_items = self.work_item_filter_service.get_closed_items(items)

        if len(closed_items) > 0:
            for value, color in zip(x_axis_lines, x_axis_line_colors):
                plt.axhline(y=value, color=color, linestyle="--", label=f"{value} Days")
        else:
            print("No closed items, skipping cycle time percentiles in WIA Scatterplot")

        plt.legend()
        self.add_logo(plt)

        # Invert x-axis
        plt.gca().invert_xaxis()

        chart_file_path = os.path.join(self.charts_folder, chart_name)
        print("Storing file at {0}".format(chart_file_path))
        plt.savefig(chart_file_path)

        if self.show_plots:
            plt.show()

    def plot_throughput_run_chart(self, items, chart_name, x_axis_unit="days"):
        print(
            "Creating Throughput Run Chart with following config: "
            "Chart Name: {0}, Unit: {1}".format(chart_name, x_axis_unit)
        )

        valid_units = ["days", "weeks", "months"]
        if x_axis_unit not in valid_units:
            raise ValueError(f"The 'x_axis_unit' parameter should be one of {valid_units}.")

        # Get only items that were closed within the specified history
        items = self.work_item_filter_service.get_closed_items(items)
        closed_dates = [item.closed_date.date() for item in items if item.closed_date]

        if not closed_dates:
            print("No closed work items for plotting throughput.")
            return

        # Set default size to be wider (10 inches width and 6 inches height in this example)
        plt.figure(figsize=(15, 9))

        throughput_counts = Counter()

        for item in closed_dates:
            if x_axis_unit == "days":
                key = item
            elif x_axis_unit == "weeks":
                key = item.isocalendar()[1]
            elif x_axis_unit == "months":
                key = item.month

            throughput_counts[key] += 1

        # Plot throughput as a bar chart
        if x_axis_unit == "days":
            x_values = sorted(set(closed_dates))
        elif x_axis_unit == "weeks":
            x_values = sorted(set(date.isocalendar()[1] for date in closed_dates))
        elif x_axis_unit == "months":
            x_values = sorted(set(date.month for date in closed_dates))

        plt.bar(
            x_values,
            [throughput_counts[key] for key in x_values],
            color="blue",
            alpha=0.7,
            label="Throughput",
        )

        plt.title("Throughput Run Chart")
        plt.xlabel(f"Work Item Closed Date ({x_axis_unit.capitalize()})")
        plt.ylabel("Number of Items Completed")
        plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.gca().set_ylim(bottom=0)
        plt.legend(loc="upper left")

        self.add_timestamp(plt)
        self.add_logo(plt)

        chart_file_path = os.path.join(self.charts_folder, chart_name)
        print("Storing file at {0}".format(chart_file_path))
        plt.savefig(chart_file_path)

        if self.show_plots:
            plt.show()

    def plot_work_in_process_run_chart(self, items, chart_name):
        print(
            "Creating Work In Process Run Chart with following config: Chart Name: {0}".format(
                chart_name
            )
        )

        relevant_items = self.work_item_filter_service.get_in_progress_items(items)

        if not relevant_items:
            print("No work items for plotting work in process.")
            return

        # Set default size to be wider (10 inches width and 6 inches height in this example)
        plt.figure(figsize=(15, 9))

        history_dates = pd.date_range(
            (self.today - timedelta(days=self.history)).date(), self.today.date()
        )

        # Count the number of items in process for each day
        wip_counts = Counter()

        for current_date in history_dates.date:
            wip_counts[current_date] = 0
            active_items = [item for item in relevant_items if item.was_active_on(current_date)]
            wip_counts[current_date] = len(active_items)

        plt.step(
            wip_counts.keys(),
            wip_counts.values(),
            where="post",
            color="orange",
            alpha=0.7,
            label="Work In Process",
        )

        plt.title("Work In Process Run Chart")
        plt.xlabel("Date")
        plt.ylabel("Number of Items In Process")
        plt.xticks(rotation=45, ha="right")  # Rotate x-axis labels for better readability
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.gca().set_ylim(bottom=0)

        date_format = DateFormatter("%Y-%m-%d")
        plt.gca().xaxis.set_major_formatter(date_format)

        plt.legend(loc="upper left")
        self.add_timestamp(plt)
        self.add_logo(plt)

        chart_file_path = os.path.join(self.charts_folder, chart_name)
        print("Storing file at {0}".format(chart_file_path))
        plt.savefig(chart_file_path)

        if self.show_plots:
            plt.show()

    def plot_work_started_vs_finished_chart(
        self, work_items, started_color, closed_color, chart_name
    ):
        print(
            "Creating Work Started vs. finished chart with following config: "
            "Chart Name: {0}, Started Color: {1}, Closed Color: {2}".format(
                chart_name, started_color, closed_color
            )
        )

        # Calculate counts based on weeks
        started_counts = {}
        closed_counts = {}

        for item in self.work_item_filter_service.get_closed_items(work_items):
            closed_date_key = item.closed_date.date().strftime("%Y-%W")
            closed_counts[closed_date_key] = closed_counts.get(closed_date_key, 0) + 1

            # Make sure we have the same keys in both dictionaries - keep the existing value
            started_counts[closed_date_key] = started_counts.get(closed_date_key, 0) + 0

        for item in self.work_item_filter_service.get_items_opened_in_period(work_items):
            started_date_key = item.started_date.date().strftime("%Y-%W")
            started_counts[started_date_key] = started_counts.get(started_date_key, 0) + 1

            # Make sure we have the same keys in both dictionaries - keep the existing value
            closed_counts[started_date_key] = closed_counts.get(started_date_key, 0) + 0

        # Sort dictionaries
        def key_function(x):
            return x[0]

        sorted_started_counts = dict(sorted(started_counts.items(), key=key_function))
        sorted_closed_counts = dict(sorted(closed_counts.items(), key=key_function))

        # Calculate the center positions for the bars
        center_positions = [x for x in range(len(started_counts))]

        # Plot the bar chart with adjusted x-axis positions
        plt.figure(figsize=(15, 9))
        bar_width = 0.35
        plt.bar(
            center_positions,
            sorted_started_counts.values(),
            width=bar_width,
            color=started_color,
            alpha=0.7,
            label="Started",
        )
        plt.bar(
            [pos + bar_width for pos in center_positions],
            sorted_closed_counts.values(),
            width=bar_width,
            color=closed_color,
            alpha=0.7,
            label="Closed",
        )

        plt.title("Work Started and Closed")
        plt.xlabel("Week of the Year")
        plt.ylabel("Number of Work Items")
        plt.gca().set_ylim(bottom=0)

        self.add_timestamp(plt)

        # Set x-axis labels based on the week of the year
        plt.xticks(
            [pos + bar_width / 2 for pos in center_positions],
            labels=sorted_started_counts.keys(),
            rotation=45,
            ha="right",
        )

        plt.legend()
        self.add_logo(plt)

        chart_file_path = os.path.join(self.charts_folder, chart_name)
        print("Storing file at {0}".format(chart_file_path))
        plt.savefig(chart_file_path)

        if self.show_plots:
            plt.show()

    def plot_estimation_vs_cycle_time_scatterplot(self, items, chart_name, estimation_unit):
        print(
            "Creating Estimation vs. Cycle Time Scatterplot with the following config: "
            "Chart Name: {0}, Estimation Unit: {1}".format(chart_name, estimation_unit)
        )

        # Ignore items without cycle time and without estimation
        closed_items = self.work_item_filter_service.get_closed_items(items)
        filtered_items = [
            item for item in closed_items if item.estimation is not None and item.estimation > 0
        ]

        cycle_times = [item.cycle_time for item in filtered_items if item.cycle_time is not None]

        if not cycle_times:
            print(
                "Either no closed work items or items don't have an estimation - "
                "skipping chart creation."
            )
            return

        items = [item for item in filtered_items if item.closed_date and item.started_date]
        cycle_times = [item.cycle_time for item in items]
        estimations = [item.estimation for item in items]

        if not cycle_times:
            print("No closed work items within the specified history for plotting.")
            return

        plt.figure(figsize=(15, 9))
        plt.scatter(estimations, cycle_times)

        if self.plot_labels:
            texts = []
            for item in items:
                text = plt.text(item.estimation, item.cycle_time, item.item_title, ha="center")
                texts.append(text)

            # Adjust text to avoid overlap
            adjustText.adjust_text(texts, arrowprops=dict(arrowstyle="-", color="k", lw=0.5))

        plt.title("Estimation vs. Cycle Time")
        plt.xlabel("Estimation ({0})".format(estimation_unit))
        plt.ylabel("Cycle Time (days)")
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
        plt.gca().set_ylim(bottom=0)

        self.add_timestamp(plt)
        self.add_logo(plt)

        chart_file_path = os.path.join(self.charts_folder, chart_name)
        print("Storing file at {0}".format(chart_file_path))
        plt.savefig(chart_file_path)

        if self.show_plots:
            plt.show()

    def plot_total_age_process_behaviour_chart(
        self, work_items, baseline_start_date, baseline_end_date, chart_name
    ):
        baseline_total_age = self.get_total_age_history_for_date_range(
            baseline_start_date, baseline_end_date, work_items
        )

        baseline_values = list(baseline_total_age.values())
        (baseline_average, unpl, lnpl) = self.caclulate_average_and_limits(baseline_values)

        start_date = self.today - timedelta(days=self.history)
        total_age_data = self.get_total_age_history_for_date_range(
            start_date, self.today, work_items
        )

        x_values = [self.today - timedelta(days=days) for days in total_age_data.keys()]
        y_values = list(total_age_data.values())

        self.plot_pbc(
            x_values,
            y_values,
            baseline_average,
            unpl,
            lnpl,
            "Total Work Item Age X Chart",
            "Date",
            "Total Age",
            chart_name,
        )

    def plot_cycle_time_process_behaviour_chart(
        self, work_items, baseline_start_date, baseline_end_date, chart_name
    ):
        baseline_cycle_time = self.get_cycle_time_history_for_date_range(
            baseline_start_date, baseline_end_date, work_items
        )

        baseline_values = [item.cycle_time for item in baseline_cycle_time.values()]
        (baseline_average, unpl, lnpl) = self.caclulate_average_and_limits(baseline_values)

        start_date = self.today - timedelta(days=self.history)
        cycle_time_data = self.get_cycle_time_history_for_date_range(
            start_date, self.today, work_items
        )

        x_values = list(cycle_time_data.keys())
        y_values = [item.cycle_time for item in cycle_time_data.values()]

        item_texts = [item.item_title for item in cycle_time_data.values()]

        self.plot_pbc(
            x_values,
            y_values,
            baseline_average,
            unpl,
            lnpl,
            "Cycle Time X Chart",
            "Item",
            "Cycle Time",
            chart_name,
            item_texts,
        )

    def plot_wip_process_behaviour_chart(
        self, work_items, baseline_start_date, baseline_end_date, chart_name
    ):
        baseline_wip = self.get_wip_history_for_date_range(
            baseline_start_date, baseline_end_date, work_items
        )

        baseline_values = list(baseline_wip.values())
        (baseline_average, unpl, lnpl) = self.caclulate_average_and_limits(baseline_values)

        start_date = self.today - timedelta(days=self.history)
        wip_data = self.get_wip_history_for_date_range(start_date, self.today, work_items)

        x_values = [self.today - timedelta(days=days) for days in wip_data.keys()]
        y_values = list(wip_data.values())

        self.plot_pbc(
            x_values,
            y_values,
            baseline_average,
            unpl,
            lnpl,
            "WIP X Chart",
            "Date",
            "WIP",
            chart_name,
        )

    def plot_throughput_process_behaviour_chart(
        self, work_items, baseline_start_date, baseline_end_date, chart_name
    ):
        baseline_closed_items = self.get_throughput_history_for_date_range(
            baseline_start_date, baseline_end_date, work_items
        )

        baseline_values = list(baseline_closed_items.values())
        (baseline_average, unpl, lnpl) = self.caclulate_average_and_limits(baseline_values)

        start_date = self.today - timedelta(days=self.history)
        throughput_data = self.get_throughput_history_for_date_range(
            start_date, self.today, work_items
        )

        x_values = [self.today - timedelta(days=days) for days in throughput_data.keys()]
        y_values = list(throughput_data.values())

        self.plot_pbc(
            x_values,
            y_values,
            baseline_average,
            unpl,
            lnpl,
            "Throughput X Chart",
            "Date",
            "Throughput",
            chart_name,
        )

    def plot_pbc(
        self,
        x_values,
        y_values,
        average,
        unpl,
        lnpl,
        title,
        x_label,
        y_label,
        chart_name,
        item_texts=[],
    ):
        # Plot data
        plt.figure(figsize=(15, 9))
        plt.plot(x_values, y_values, marker="o", linestyle="-", color="b")

        plt.gca().set_ylim(bottom=0)  # Set y-axis minimum to 0

        # Plot baseline average, unpl, and lnpl as horizontal lines
        plt.axhline(y=average, color="r", linestyle="--", label="Average")
        plt.axhline(y=unpl, color="g", linestyle="--", label="Upper Natural Process Limit (UNPL)")

        if lnpl > 0:
            plt.axhline(
                y=lnpl, color="y", linestyle="--", label="Lower Natural Process Limit (LNPL)"
            )

        # Set x-axis label and rotate x-axis ticks for better readability
        plt.xlabel(x_label)
        plt.xticks(rotation=45)

        # Set y-axis label
        plt.ylabel(y_label)

        if self.plot_labels:
            texts = []
            for index in range(len(item_texts)):
                text = plt.text(x_values[index], y_values[index], item_texts[index], ha="center")
                texts.append(text)

            # Adjust text to avoid overlap
            adjustText.adjust_text(texts, arrowprops=dict(arrowstyle="-", color="k", lw=0.5))

        # Set chart title and legend
        plt.title(title)
        plt.legend()

        self.add_timestamp(plt)
        self.add_logo(plt)

        chart_file_path = os.path.join(self.charts_folder, chart_name)
        print("Storing file at {0}".format(chart_file_path))
        plt.savefig(chart_file_path)

        if self.show_plots:
            plt.show()

    def get_cycle_time_history_for_date_range(self, start_date, end_date, work_items):
        filtered_items = [
            item
            for item in work_items
            if item.cycle_time and start_date <= item.closed_date <= end_date
        ]

        # Sort the filtered items by closed_date
        sorted_items = sorted(filtered_items, key=lambda item: item.closed_date)

        # Create a dictionary with integer keys starting from 0
        sorted_items_dict = {index: item for index, item in enumerate(sorted_items)}

        return sorted_items_dict

    def get_total_age_history_for_date_range(self, start_date, end_date, work_items):
        total_age_per_day = {}

        # Iterate through each day from start_date to end_date
        current_date = start_date
        day_count = 0
        while current_date <= end_date:
            total_age_per_day[day_count] = 0

            # Iterate through each item
            for item in work_items:
                # Check if the item was started but not closed on the current day
                if item.was_active_on(current_date.date()):
                    # Calculate the delta between the current date and the item's started date
                    delta_days = item.get_work_item_age(current_date.date())

                    # Increment total age by the delta
                    total_age_per_day[day_count] += delta_days

            # Move to the next day
            current_date += timedelta(days=1)
            day_count += 1

        return total_age_per_day

    def get_wip_history_for_date_range(self, start_date, end_date, work_items):
        count_per_day = {}

        # Iterate through each day from start_date to end_date
        current_date = start_date
        day_count = 0  # Initialize day count
        while current_date <= end_date:
            count_per_day[day_count] = 0  # Initialize count to 0 for the current day

            # Iterate through each item
            for item in work_items:
                if item.was_active_on(current_date.date()):
                    count_per_day[day_count] += 1

            # Move to the next day
            current_date += timedelta(days=1)
            day_count += 1  # Increment day count

        return count_per_day

    def get_throughput_history_for_date_range(self, start_date, end_date, work_items):
        closed_items_count = {}

        date_range = (end_date - start_date).days + 1

        for index in range(date_range):
            closed_items_count[index] = 0

        for item in work_items:
            if item.closed_date and start_date <= item.closed_date <= end_date:
                index = (item.closed_date - start_date).days

                closed_items_count[index] += 1

        return closed_items_count

    def caclulate_average_and_limits(self, baseline_values):
        baseline_average = self.calculate_mean(baseline_values)
        moving_ranges = self.calculate_moving_ranges(baseline_values)
        moving_range_mean = self.calculate_mean(moving_ranges)
        (unpl, lnpl) = self.calculate_natural_process_limits(baseline_average, moving_range_mean)
        return (baseline_average, unpl, lnpl)

    def calculate_mean(self, values):
        mean = 0

        if len(values) > 0:
            mean = sum(values) / len(values)

        return mean

    def calculate_moving_ranges(self, values):
        moving_ranges = []
        for i in range(1, len(values)):
            moving_range = abs(values[i] - values[i - 1])
            moving_ranges.append(moving_range)
        return moving_ranges

    def calculate_natural_process_limits(self, baseline_average, baseline_moving_range_average):
        unpl = baseline_average + (2.66 * baseline_moving_range_average)
        lnpl = baseline_average - (2.66 * baseline_moving_range_average)

        if lnpl < 0:
            lnpl = 0

        return (unpl, lnpl)

    def add_timestamp(self, plt):
        plt.text(
            1,
            1.02,
            f"Generated on {self.current_date}",
            transform=plt.gca().transAxes,
            fontsize=10,
            ha="right",
            va="top",
        )

    def add_logo(self, plt):
        # Add logo
        imagebox = OffsetImage(self.logo, zoom=0.48)
        ab = AnnotationBbox(
            imagebox, (0.065, 1.08), xycoords="axes fraction", frameon=False, box_alignment=(1, 1)
        )
        plt.gca().add_artist(ab)
