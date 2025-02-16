import os
import pytest
from datetime import datetime, timedelta
from tests.utils.test_utils import compare_images

from flowpulse.services.WorkItemFilterService import WorkItemFilterService
from flowpulse.services.FlowMetricsService import FlowMetricsService
from flowpulse.WorkItem import WorkItem
import shutil


class TestFlowMetricsService:
    @pytest.fixture
    def setup_service(self):
        # Create a fixed test configuration
        self.show_plots = False
        self.charts_folder = os.path.join("tests", "test_charts")
        self.baseline_folder = os.path.join("tests", "baseline_charts")
        self.history = 30
        self.today = datetime(2024, 1, 1)

        self.service = FlowMetricsService(
            self.show_plots,
            self.charts_folder,
            WorkItemFilterService(self.today, self.history),
            self.history,
            True,
            self.today,
        )

        # Create test directories if they don't exist
        os.makedirs(self.charts_folder, exist_ok=True)
        os.makedirs(self.baseline_folder, exist_ok=True)

        return self.service

    @pytest.fixture
    def sample_work_items(self):
        # Create a diverse set of work items with realistic dates and cycle times
        items = [
            # Completed items with varying cycle times
            WorkItem(
                "PROJ-101",
                "Update user authentication",
                datetime(2023, 12, 20),
                datetime(2023, 12, 22),
                3,  # Story points
            ),
            WorkItem(
                "PROJ-102",
                "Fix critical security vulnerability",
                datetime(2023, 12, 15),
                datetime(2023, 12, 16),
                5,  # Urgent fix, completed quickly
            ),
            WorkItem(
                "PROJ-103",
                "Implement new dashboard features",
                datetime(2023, 12, 10),
                datetime(2023, 12, 25),
                8,  # Large feature, took longer
            ),
            WorkItem(
                "PROJ-104",
                "Database optimization",
                datetime(2023, 12, 18),
                datetime(2023, 12, 28),
                5,  # Medium complexity
            ),
            WorkItem(
                "PROJ-105",
                "API documentation update",
                datetime(2023, 12, 26),
                datetime(2023, 12, 27),
                2,  # Small task
            ),
            WorkItem(
                "PROJ-106",
                "Mobile responsiveness fixes",
                datetime(2023, 12, 5),
                datetime(2023, 12, 15),
                3,  # Medium duration
            ),
            # In-progress items with different ages
            WorkItem(
                "PROJ-107",
                "Cloud migration - Phase 1",
                datetime(2023, 12, 10),
                None,
                13,  # Large, long-running item
            ),
            WorkItem(
                "PROJ-108",
                "Performance monitoring setup",
                datetime(2023, 12, 28),
                None,
                5,  # Recently started
            ),
            WorkItem(
                "PROJ-109",
                "User feedback integration",
                datetime(2023, 12, 22),
                None,
                3,  # Medium duration in-progress
            ),
            # Not started item
            WorkItem("PROJ-110", "Future feature planning", None, None, 8),  # Not yet started
            # Additional completed items
            WorkItem(
                "PROJ-111",
                "Bug fix: login page",
                datetime(2023, 12, 29),
                datetime(2023, 12, 30),
                1,  # Quick fix
            ),
            WorkItem(
                "PROJ-112",
                "Email template redesign",
                datetime(2023, 12, 12),
                datetime(2023, 12, 19),
                5,  # Week-long task
            ),
        ]

        return items

    def setup_method(self):
        # Track if the test passed
        self.test_passed = True

    def compare_images(self, test_image_path, baseline_image_name):
        baseline_path = os.path.join(self.baseline_folder, baseline_image_name)

        # Ensure both images exist
        if not os.path.exists(test_image_path):
            pytest.fail(f"Test image not found: {test_image_path}")
        if not os.path.exists(baseline_path):
            # Copy the test image to create a new baseline
            shutil.copy2(test_image_path, baseline_path)
            pytest.fail(f"Baseline image not found: {baseline_path}")

        return compare_images(test_image_path, baseline_path)

    def test_cycle_time_scatterplot(self, setup_service, sample_work_items):
        chart_name = "test_cycle_time_scatter.png"
        chart_path = os.path.join(self.charts_folder, chart_name)

        self.service.plot_cycle_time_scatterplot(
            items=sample_work_items,
            percentiles=[50, 85],
            percentile_colors=["green", "red"],
            chart_name=chart_name,
            trend_settings=[85, 7, "blue"],
        )

        assert self.compare_images(chart_path, chart_name)

    def test_work_item_age_scatterplot(self, setup_service, sample_work_items):
        chart_name = "test_work_item_age.png"
        chart_path = os.path.join(self.charts_folder, chart_name)

        self.service.plot_work_item_age_scatterplot(
            items=sample_work_items,
            x_axis_lines=[5, 10],
            x_axis_line_colors=["green", "red"],
            chart_name=chart_name,
        )

        assert self.compare_images(chart_path, chart_name)

    def test_throughput_run_chart(self, setup_service, sample_work_items):
        chart_name = "test_throughput.png"
        chart_path = os.path.join(self.charts_folder, chart_name)

        self.service.plot_throughput_run_chart(
            items=sample_work_items, chart_name=chart_name, x_axis_unit="days"
        )

        assert self.compare_images(chart_path, chart_name)

    def test_work_in_process_run_chart(self, setup_service, sample_work_items):
        chart_name = "test_wip.png"
        chart_path = os.path.join(self.charts_folder, chart_name)

        self.service.plot_work_in_process_run_chart(items=sample_work_items, chart_name=chart_name)

        assert self.compare_images(chart_path, chart_name)

    def test_work_started_vs_finished_chart(self, setup_service, sample_work_items):
        chart_name = "test_started_vs_finished.png"
        chart_path = os.path.join(self.charts_folder, chart_name)

        self.service.plot_work_started_vs_finished_chart(
            work_items=sample_work_items,
            started_color="orange",
            closed_color="green",
            chart_name=chart_name,
        )

        assert self.compare_images(chart_path, chart_name)

    def test_estimation_vs_cycle_time_scatterplot(self, setup_service, sample_work_items):
        chart_name = "test_estimation_vs_cycle_time.png"
        chart_path = os.path.join(self.charts_folder, chart_name)

        self.service.plot_estimation_vs_cycle_time_scatterplot(
            items=sample_work_items, chart_name=chart_name, estimation_unit="points"
        )

        assert self.compare_images(chart_path, chart_name)

    def test_process_behaviour_charts(self, setup_service, sample_work_items):
        baseline_start = self.today - timedelta(days=30)
        baseline_end = self.today - timedelta(days=10)

        charts = [
            ("test_pbc_total_age.png", self.service.plot_total_age_process_behaviour_chart),
            ("test_pbc_cycle_time.png", self.service.plot_cycle_time_process_behaviour_chart),
            ("test_pbc_wip.png", self.service.plot_wip_process_behaviour_chart),
            ("test_pbc_throughput.png", self.service.plot_throughput_process_behaviour_chart),
        ]

        for chart_name, plot_function in charts:
            chart_path = os.path.join(self.charts_folder, chart_name)

            plot_function(
                work_items=sample_work_items,
                baseline_start_date=baseline_start,
                baseline_end_date=baseline_end,
                chart_name=chart_name,
            )

            assert self.compare_images(chart_path, chart_name)

    def teardown_method(self):
        # Only clean up test charts if the test passed
        if self.test_passed and os.path.exists(self.charts_folder):
            for file in os.listdir(self.charts_folder):
                os.remove(os.path.join(self.charts_folder, file))
            os.rmdir(self.charts_folder)
        elif not self.test_passed:
            print(f"Test failed - Generated charts preserved in: {self.charts_folder}")
