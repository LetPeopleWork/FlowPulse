import pytest
import os
from datetime import datetime
from flowpulse.services.WorkItemServiceFactory import WorkItemServiceFactory
from flowpulse.services.JiraWorkItemService import JiraWorkItemService
from flowpulse.services.AzureDevOpsWorkItemService import AzureDevOpsWorkItemService
from flowpulse.services.CsvService import CsvService


class TestWorkItemServiceFactory:
    @pytest.fixture
    def factory(self):
        return WorkItemServiceFactory()

    @pytest.fixture
    def mock_data_sources(self):
        azure_token = os.environ.get("AzureDevOpsLighthouseIntegrationTestToken", "default_token")

        return [
            {
                "name": "jira",
                "url": "https://letpeoplework.atlassian.net",
                "username": "user",
                "apiToken": "token",
                "estimationField": "story_points",
                "itemQuery": "project = TEST",
                "anonymizeLabel": False,
            },
            {
                "name": "azuredevops",
                "organizationUrl": "https://dev.azure.com/huserben",
                "apiToken": azure_token,
                "estimationField": "story_points",
                "itemQuery": "SELECT * FROM WorkItems",
            },
            {
                "name": "csv",
                "fileName": "tests/testdata.csv",
                "delimiter": ",",
                "startedDateColumn": "Started",
                "closedDateColumn": "Closed",
                "startDateFormat": "%Y-%m-%d",
                "closedDateFormat": "%Y-%m-%d",
                "estimationColumn": "Points",
                "itemTitleColumn": "Title",
            },
        ]

    def test_create_service_no_data_source_type(self, factory):
        """Test creating service with no data source type raises ValueError"""
        with pytest.raises(ValueError) as exc:
            factory.create_service(None, [], 30, datetime.now())
        assert "No data source specified" in str(exc.value)

    def test_create_service_empty_data_sources(self, factory):
        """Test creating service with empty data sources raises ValueError"""
        with pytest.raises(ValueError) as exc:
            factory.create_service("jira", [], 30, datetime.now())
        assert "No data sources specified" in str(exc.value)

    def test_create_service_invalid_type(self, factory, mock_data_sources):
        """Test creating service with invalid type raises ValueError"""
        with pytest.raises(ValueError) as exc:
            factory.create_service("invalid", mock_data_sources, 30, datetime.now())
        assert "No data source configuration found" in str(exc.value)

    def test_create_jira_service(self, factory, mock_data_sources):
        """Test creating Jira service returns JiraWorkItemService instance"""
        service = factory.create_service("jira", mock_data_sources, 30, datetime.now())
        assert isinstance(service, JiraWorkItemService)

    def test_create_azure_devops_service(self, factory, mock_data_sources):
        """Test creating Azure DevOps service returns AzureDevOpsWorkItemService instance"""
        service = factory.create_service("azuredevops", mock_data_sources, 30, datetime.now())
        assert isinstance(service, AzureDevOpsWorkItemService)

    def test_create_csv_service(self, factory, mock_data_sources):
        """Test creating CSV service returns CsvService instance"""
        today = datetime.now()
        service = factory.create_service("csv", mock_data_sources, 30, today)
        assert isinstance(service, CsvService)
