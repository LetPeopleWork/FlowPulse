---
title: Configuration
parent: Overview
layout: home
nav_order: 2
---

The configuration can be made in one json file. Every version of flowpulse comes with an [ExampleConfig.json] that will be copied to your directory if no other configurations are specified or found in the folder.

{: .important}
You **must** follow the json specification for any changes you make in this file. Double Quotes (") as well as backslashes (\\) cannot be written in json like this. You have to "escape" it by prepending a \\. Thus if you want to write a ", you have to type \\". If you want to use a backslash, you must write \\ \\. Please reference the example configurations default values. As your queries will most likely include those, please keep this in mind.

{: .recommendation}
If you get an error `Error reading config file`, try to validate your json file with a [Json Validator](https://jsonlint.com/).

The configuration consists out of four sections:

- TOC
{:toc}


# General

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| datasource     | Which Work Tracking System to use.                         | Either "Jira" or "Azure DevOps" |
| ChartsFolder           | Folder path for the folder where the charts should be saved. Can be relative to the script location (like the default) or a full path to a folder. Folder does not need to exist, it will be created as part of the script.               | Charts             |
| ShowPlots              | If set to true, the script will stop and show you an interactive version of the chart before continuing.                | false              |
rawDataCSV              | If specified, the work items returned by the query will additionally be stored in a csv file within the charts folder.                | workitems.csv     |
today              | Specify to set a different "end date" for your charts and forecasts than today. Specify dates in the format "YYYY-MM-dd", for example 2024-08-19 for the 19th of August 2024. This setting helps you generate charts and forecasts for past date intervals, for example if you want to recreate charts for a given month in the past. The history parameter of the different charts uses the "Today" date as reference, and will "go back" from this one.                | null              |

# Data Sources

### Jira Settings
In order use `flowpulse` with Jira, you must specify against which Jira instance you are working. For this you need a url, as well as a [Personal Access Token](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html) and your username. Furthermore you have to specify a query that gets the items of the team(s) you are interested in as well as how many days into the past you are interested in. Last but not least, you can specify which field you are using for estimates. The queries are written in [JQL](https://www.atlassian.com/blog/jira/jql-the-most-flexible-way-to-search-jira-14).

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| url           | The url to your Jira instance. Replace _YourOrg_ with your actual organization name.               | https://YourOrg.atlassian.net             |
| username           | The user that shall be used for exeucting the queries.               |              |
| apiToken              | [Personal Access Token](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html) to access the data in your organization             | ""              |
| itemQuery           | The query to get your teams items. Note that this should contain all items that are relevant for your team, closed, in progress, and not started. Check out the [JQL reference](https://www.atlassian.com/blog/jira/jql-the-most-flexible-way-to-search-jira-14) if you need support.             | issuetype in (\"Story\", \"Bug\") AND project = \"YourProject\" AND labels = \"YourTeamLabel\"             |
| history           | Number of days you look back for items (e.g. "90" for last 90 days), or date in the format "YYYY-MM-dd" (2024-08-19) to include all items since that date.               | 90             |
| estimationField           | Which field is holding the estimates. This might be a custom field, depending on your process.            | timetracking.originalEstimate             |
| anonymizeLabel           | Anonymizes the labels in the charts, by not using the full issue key, but just the numbers.            | true or false             |


### Azure DevOps Settings
In order use `flowpulse` with Azure DevOps, you must specify against which Azure DevOps organization you are working. For this you need a url, as well as a [Personal Access Token](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows). Furthermore you have to specify a query that gets the items of the team(s) you are interested in as well as how many days into the past you are interested in. Last but not least, you can specify which field you are using for estimates. The queries are written in [WIQL](https://learn.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops).


| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| organizationUrl           | The url to your Azure DevOps Organization. Replace _YourOrg_ with your actual organization name.               | https://dev.azure.com/YourOrg             |
| apiToken              | [Personal Access Token](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows) to access the data in your organization             | ""              |
| itemQuery           | The query to get your teams items. Note that this should contain all items that are relevant for your team, closed, in progress, and not started. Check out the [WIQL reference](https://learn.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops) if you need support.             | ([System.WorkItemType] = \"User Story\" or [System.WorkItemType] = \"Bug\") AND [System.TeamProject] == \"Your Project\" AND [System.AreaPath] UNDER \"Team Project\\\\Team Name\"             |
| history           | Number of days you look back for items (e.g. "90" for last 90 days), or date in the format "YYYY-MM-dd" (2024-08-19) to include all items since that date.            | 90             |
| estimationField           | Which field is holding the estimates. You can see the "reference Name" for the fields if you browse to *https://dev.azure.com/%7Borganization%7D/%7Bproject%7D/_apis/wit/fields?api-version=7.1-preview.3* - and insert your organization and project            | Microsoft.VSTS.Scheduling.StoryPoints             |

# Charts

# Forecasts

### Forecast Settings
You can add one or more forecasts. Forecasts need two inputs: The remaining items you want to forecast (when will they be done?) and a target date (how much can we get done till then). The target date is specified either as a date in the format *YYYY-mm-dd* or as number. If you specify a number, it will use the date that is this amount of days in the future. To get the remaining items, you specify a query that returns all items that are not yet done and you want to forecast. You can use all filters JQL has to offer, for example filtering by area path, tag, iteration path, or anything else.

If you don't provide a *target date*, no "How Many" simulation will be run. If you don't provide a *remaining Backlog Query*, no "When" simulation will be run. If you provide both, you'll get a on top a likelihood of reaching the target date with the remaining backlog.

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| name           | The name of your Forecast.               | "Release 23.44" or "Sprint Goal"             |
| remainingBacklogQuery           | The query to get the remaining items for your forecast. Note that this should contain all items that are relevant for your forecast, so most likely you want to filter out closed and removed items. This is either a JQL query if you are using Jira or a WIQL query in the case of Azure DevOps.           | issuetype in (\"Story\", \"Bug\") AND project = \"YourProject\" AND status not in (\"Done\") AND fixVersion = \"Release 24.10\" |
| targetDate           | Either the date in *YYYY-mm-dd* format or the number of days in future               | "2024-10-31" / 14             |

#### Skip Forecasts
If you don't want to run any forecasts, just remove all forecasts, so that your config looks like this:
```
"forecasts":[
    ],
```

### Chart Settings
Every chart can be configured with different settings. You can also switch off the generation of a sepcific chart by setting `generate: false`.
You can find detailed information to the possible chart configurations in [FlowMetricsCSV](https://github.com/LetPeopleWork/FlowMetricsCSV?tab=readme-ov-file#cycle-time-scatter-plot).


After you configured `flowpulse` with your queries and with your token, you are ready to go. simply run `flowpulse --ConfigFileNames "YourConfig.json"`. It will generate all the charts according to your configurations and will show you your forecasts in the commandline.

## How to use the created charts?
You find more information on this in the [wiki](https://github.com/LetPeopleWork/FlowMetricsCSV/wiki)

## How to build your own Applications on Top of this Package?
If you have additional demands, like running the forecasts on a regular base and pushing the results somewhere (like in a database) instead of just displaying it in the commandline, you can build your own python application on top.

After you installed the package, you can include the following services and then run your own applications on top:
```
from FlowMetricsCSV.FlowMetricsService import FlowMetricsService
from MonteCarloCSV.MonteCarloService import MonteCarloService
from flowpulse.JiraWorkItemService import JiraWorkItemService
from flowpulse.AzureDevOpsWorkItemService import AzureDevOpsWorkItemService
```

You can create the various services and provide the necessary configuration as it best fits you:
```
jira_work_item_service = JiraWorkItemService(jira_url, jira_username, jira_api_token, jira_estimation_field, history_in_days)
azure_devops_work_item_service = AzureDevOpsWorkItemService(ado_org_url, ado_api_token, ado_estimation_field, history_in_days)
flow_metrics_service = FlowMetricsService(False, "Charts")
monte_carlo_service = MonteCarloService(history_in_days, False)
```

Using those services, you can get the data from Jira via JQL, transform it to create your charts, and run forecasts:
```
work_items = jira_work_item_service.get_items_via_query(item_query)
work_items = azure_devops_work_item_service.get_items_via_query(item_query)
work_items = [item for item in work_items if item.started_date is not None]

flow_metrics_service.plot_cycle_time_scatterplot(work_items, 14, percentiles, percentile_colors, "Cycle Time Scatterplot")

closed_items = [item for item in work_items if item.closed_date is not None]
throughput_history = monte_carlo_service.create_closed_items_history(closed_items)

(percentile_50, percentile_70, percentile_85, percentile_95) = monte_carlo_service.how_many(target_date, throughput_history)

(predicted_date_50, predicted_date_70, predicted_date_85, predicted_date_95, target_date_likelyhood) = monte_carlo_service.when(remaining_items, throughput_history, target_date)
```

See [Github](https://github.com/LetPeopleWork/flowpulse/blob/main/Examples/use_individual_services.py) for a full example of how you can use this.