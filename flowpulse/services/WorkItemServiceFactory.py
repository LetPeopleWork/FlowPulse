from .JiraWorkItemService import JiraWorkItemService
from .AzureDevOpsWorkItemService import AzureDevOpsWorkItemService
from .CsvService import CsvService

class WorkItemServiceFactory:
    def create_service(self, config, history_in_days, today):
        data_source = config["general"]["datasource"].lower().replace(" ", "")
        
        print(f"Using the following source for the work items: {data_source}")
        
        if data_source == "jira":
            return self._create_jira_service(config, history_in_days, today)
        elif data_source == "azuredevops":
            return self._create_azure_devops_service(config, history_in_days, today)
        elif data_source == "csv":
            return self._create_csv_service(config, history_in_days, today)
        else:
            raise ValueError(f"Work Tracking System '{config['general']['datasource']}' not supported. Supported values are 'Jira', 'Azure DevOps' and 'CSV'")

    def _create_jira_service(self, config, history_in_days, today):
        jira_config = config["jira"]
        anonymize_label = jira_config.get("anonymizeLabel", False)
        return JiraWorkItemService(
            jira_config["url"],
            jira_config["username"],
            jira_config["apiToken"],
            jira_config["estimationField"],
            history_in_days,
            anonymize_label,
            today,
            jira_config["itemQuery"]
        )

    def _create_azure_devops_service(self, config, history_in_days, today):
        azure_config = config["azureDevOps"]
        return AzureDevOpsWorkItemService(
            azure_config["organizationUrl"],
            azure_config["apiToken"],
            azure_config["estimationField"],
            history_in_days,
            today,
            azure_config["itemQuery"]
        )

    def _create_csv_service(self, config, history_in_days, today):
        csv_config = config["csv"]
        return CsvService(
            csv_config["fileName"],
            csv_config["delimeter"],
            csv_config["startedDateColumn"],
            csv_config["closedDateColumn"],
            csv_config["startDateFormat"],
            csv_config["closedDateFormat"],
            csv_config["estimationColumn"],
            csv_config["itemTitleColumn"],
            history_in_days,
            today
        )