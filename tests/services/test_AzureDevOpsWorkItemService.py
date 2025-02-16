import pytest
import os
from datetime import datetime, timezone
from flowpulse.services.AzureDevOpsWorkItemService import AzureDevOpsWorkItemService


class TestAzureDevOpsWorkItemService:
    @pytest.fixture
    def service(self):
        token = os.environ.get("AzureDevOpsLighthouseIntegrationTestToken", "default_token")
        print(token)
        return AzureDevOpsWorkItemService(
            "https://dev.azure.com/huserben",
            token,
            "Microsoft.VSTS.Scheduling.Size",
            '[System.WorkItemType] = "User Story" '
            'AND [System.State] <> "Removed" '
            'AND [Microsoft.VSTS.Common.ClosedDate] >= "2024-01-01" '
            'AND [Microsoft.VSTS.Common.ClosedDate] <= "2024-01-31"',
        )

    def test_get_work_items(self, service):
        """Test get work items from Azure DevOps"""
        items = service.get_items()
        assert isinstance(items, list)
        if len(items) > 0:
            assert all(hasattr(item, "id") for item in items)
            assert all(hasattr(item, "title") for item in items)
            assert all(hasattr(item, "state") for item in items)
            assert all(hasattr(item, "started_date") for item in items)
            assert all(hasattr(item, "closed_date") for item in items)
            assert all(hasattr(item, "estimation") for item in items)

    def test_fetch_work_items_with_dates(self, service):
        """Test that fetched work items have valid dates within the specified range"""
        items = service.get_items()
        start_date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        end_date = datetime(2024, 1, 31, tzinfo=timezone.utc)

        for item in items:
            if item.started_date:
                assert start_date <= item.started_date <= end_date
            if item.closed_date:
                assert start_date <= item.closed_date <= end_date

    def test_fetch_work_items_with_estimation(self, service):
        """Test that fetched work items have estimation values"""
        items = service.get_items()
        for item in items:
            assert isinstance(item.estimation, (int, float, type(None)))
