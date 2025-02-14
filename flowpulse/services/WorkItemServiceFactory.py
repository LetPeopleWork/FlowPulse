from .JiraWorkItemService import JiraWorkItemService
from .AzureDevOpsWorkItemService import AzureDevOpsWorkItemService
from .CsvService import CsvService

class WorkItemServiceFactory:
    def create_service(self, config, history_in_days, today):
        work_tracking_system = config["general"]["datasource"].lower().replace(" ", "")
        
        print(f"Using the following source for the work items: {work_tracking_system}")
        
        if work_tracking_system == "jira":
            return self._create_jira_service(config)
        elif work_tracking_system == "azuredevops":
            return self._create_azure_devops_service(config)
        elif work_tracking_system == "csv":
            return self._create_csv_service(config, history_in_days, today)
        else:
            raise ValueError(f"Work Tracking System '{config['general']['datasource']}' not supported. Supported values are 'Jira', 'Azure DevOps' and 'CSV'")

    def _create_jira_service(self, config):
        jira_config = config["jira"]
        anonymize_label = jira_config.get("anonymizeLabel", False)
        return JiraWorkItemService(
            jira_config["url"],
            jira_config["username"],
            jira_config["apiToken"],
            jira_config["estimationField"],
            anonymize_label,
            jira_config["itemQuery"]
        )

    def _create_azure_devops_service(self, config):
        azure_config = config["azureDevOps"]
        return AzureDevOpsWorkItemService(
            azure_config["organizationUrl"],
            azure_config["apiToken"],
            azure_config["estimationField"],
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