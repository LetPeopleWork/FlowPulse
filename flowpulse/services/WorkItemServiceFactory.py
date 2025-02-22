from .JiraWorkItemService import JiraWorkItemService
from .AzureDevOpsWorkItemService import AzureDevOpsWorkItemService
from .CsvService import CsvService


class WorkItemServiceFactory:
    def create_service(self, data_source_type, data_sources, history_in_days, today):
        if not data_source_type:
            raise ValueError("No data source specified in the configuration file")

        if len(data_sources) < 1:
            raise ValueError("No data sources specified in the configuration file")

        data_source = next(
            (ds for ds in data_sources if ds["name"].lower() == data_source_type.lower()), None
        )

        if not data_source:
            raise ValueError(f"No data source configuration found for type: {data_source_type}")

        print(f"Using the following source for the work items: {data_source_type}")

        match data_source_type:
            case "jira":
                return self._create_jira_service(data_source)
            case "azuredevops":
                return self._create_azure_devops_service(data_source)
            case "csv":
                return self._create_csv_service(data_source, history_in_days, today)
            case _:
                raise ValueError(
                    f"Work Tracking System '{data_source_type}' not supported. "
                    "Supported values are 'Jira', 'Azure DevOps' and 'CSV'"
                )

    def _create_jira_service(self, jira_config):
        anonymize_label = jira_config.get("anonymizeLabel", False)
        return JiraWorkItemService(
            jira_config["url"],
            jira_config["username"],
            jira_config["apiToken"],
            jira_config["estimationField"],
            anonymize_label,
            jira_config["itemQuery"],
        )

    def _create_azure_devops_service(self, azure_config):
        return AzureDevOpsWorkItemService(
            azure_config["organizationUrl"],
            azure_config["apiToken"],
            azure_config["estimationField"],
            azure_config["itemQuery"],
        )

    def _create_csv_service(self, csv_config, history_in_days, today):
        return CsvService(
            csv_config["fileName"],
            csv_config["delimiter"],
            csv_config["startedDateColumn"],
            csv_config["closedDateColumn"],
            csv_config["startDateFormat"],
            csv_config["closedDateFormat"],
            csv_config["estimationColumn"],
            csv_config["itemTitleColumn"],
            history_in_days,
            today,
        )
