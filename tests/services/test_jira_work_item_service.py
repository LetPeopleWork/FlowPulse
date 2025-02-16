import os
import pytest
from flowpulse.services.JiraWorkItemService import JiraWorkItemService


@pytest.fixture
def jira_service():
    token = os.getenv("JiraLighthouseIntegrationTestToken", "default_token")

    return JiraWorkItemService(
        "https://letpeoplework.atlassian.net",
        "benjhuser@gmail.com",
        token,
        "timetracking.originalEstimate",
        False,
        'issuetype in ("Story", "Bug") AND project = "LGHTHSDMO" '
        'AND status changed during ("2025-01-01","2025-01-31")',
    )


def test_get_work_items(jira_service):
    items = jira_service.get_items()

    assert items is not None
    assert len(items) > 0
    assert all(hasattr(item, "id") for item in items)


def test_estimation_field(jira_service):
    items = jira_service.get_items()
    items_with_estimates = [item for item in items if item.estimation is not None]

    if items_with_estimates:
        assert isinstance(items_with_estimates[0].estimation, (int, float))
