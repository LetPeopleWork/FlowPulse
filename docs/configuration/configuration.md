---
title: Configuration
parent: Overview
layout: home
nav_order: 2
---

The configuration can be made in one json file. Every version of flowpulse comes with an [ExampleConfig.json](https://github.com/LetPeopleWork/FlowPulse/blob/main/flowpulse/ExampleConfig.json) that will be copied to your directory if no other configurations are specified or found in the folder.

{: .important}
You **must** follow the json specification for any changes you make in this file. Double Quotes (") as well as backslashes (\\) cannot be written in json like this. You have to "escape" it by prepending a \\. Thus if you want to write a ", you have to type \\". If you want to use a backslash, you must write \\ \\. Please reference the example configurations default values. As your queries will most likely include those, please keep this in mind.

{: .recommendation}
If you get an error `Error reading config file`, try to validate your json file with a [Json Validator](https://jsonlint.com/).

The configuration consists out of four sections:

- TOC
{:toc}


# General
The following options are available for the general FlowPulse configuration:

| Name                   | Description                          | Potential Values      |
|------------------------|---------------------------|-----------------------|
| datasource     | Which source for the data to use. Selection of available [Data Sources](#data-sources).                         | *CSV*, *Jira*, or *AzureDevOps* |
| ChartsFolder           | Folder path for the folder where the charts should be saved. Can be relative to the script location or a full path to a folder. Folder does not need to exist, it will be created as part of the script.               | *D:/FlowPulse/Charts* or *Charts*             |
| ShowPlots              | If set to true, the script will stop and show you an interactive version of the chart before continuing.                | *false* or *true*              |
rawDataCSV              | If specified, the work items returned by the query will additionally be stored in a csv file within the *Charts folder*.                | *workitems.csv* or *null*     |
plotLabels              | If set to true, the charts will show the Work Item ID on the chart. Disable if you don't want to show this or if you have too many data points for it to be readable.                | *true* or *false*     |
history              | How *far back* you want to go with your data from today. For example a value of *30* would mean that you look at the last 30 days. This setting applies to all charts and also for the Throughput used for the Forecasts.            | Any positive number     |
today              | Specify to set a different "end date" for your charts and forecasts than today. Specify dates in the format "YYYY-MM-dd", for example 2024-08-19 for the 19th of August 2024. This setting helps you generate charts and forecasts for past date intervals, for example if you want to recreate charts for a given month in the past. The history parameter uses the "Today" date as reference, and will "go back" from this one.                | *null* or date in form *YYYY-MM-dd*              |

# Data Sources
Under *dataSources* you can define what is your datasource. The [ExampleConfig.json](https://github.com/LetPeopleWork/FlowPulse/blob/main/flowpulse/ExampleConfig.json) will contain all available dataSources with their settings. However, you will only need one in your configuration (the one you select in [General](#general)), and can safely delete the other ones to keep your configuration lean.

{: .recommendation}
This section is just about how to configure the various data sources. If you want more details about them, check out the [dedicated page](../datasource/datasources.html).

Each data source comes with different configuration options. See the following chapters for details on each supported data source.

{: .note}
Every data source has a *name* property. The value you specify for the data source in [General](#general) must match the value of the *name*. We advice to keep the default names, but if you want, you can rename them as well. Who are we to judge?

## CSV
If you want to use CSV files as your data source, you need to specify how your CSV file is structured. This includes which columns contain the relevant dates, and how these dates are formatted.

| Name                   | Description                          | Potential Values      |
|------------------------|--------------------------------------|--------------------|
| fileName           | Name of the CSV file containing your work item data               | ExampleFile.csv             |
| delimeter           | The character used to separate columns in your CSV file               | ";" or ","              |
| startedDateColumn           | Name of the column that contains the date when work was started on an item               | "Activated Date", "Started Date"             |
| closedDateColumn           | Name of the column that contains the date when work was completed               | "Closed Date", "Completed Date"             |
| startDateFormat           | Format string for parsing the start date. Uses Python's datetime format codes               | "%m/%d/%Y", "%Y-%m-%d", "%d.%m.%Y"             |
| closedDateFormat           | Format string for parsing the close date. If empty, uses same format as startDateFormat               | "" or date format (see *startDateFormat*)             |
| estimationColumn           | Name of the column containing work item estimates               | "Story Points", "Estimate"             |
| itemTitleColumn           | Name of the column containing the work item identifier               | "ID", "Key"             |

## Jira
In order use `flowpulse` with Jira, you must specify against which Jira instance you are working. For this you need a url, as well as a [Personal Access Token](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html) and your username. Furthermore you have to specify a query that gets the items of the team(s) you are interested in as well as how many days into the past you are interested in. Last but not least, you can specify which field you are using for estimates. The queries are written in [JQL](https://www.atlassian.com/blog/jira/jql-the-most-flexible-way-to-search-jira-14).

| Name                   | Description                          | Potential Values      |
|------------------------|--------------------------------------|--------------------|
| url           | The url to your Jira instance. Replace _YourOrg_ with your actual organization name.               | https://YourOrg.atlassian.net             |
| username           | The user that shall be used for exeucting the queries.               |              |
| apiToken              | [API Token](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) to access the data in your organization             | ""              |
| itemQuery           | The query to get your teams items. Note that this should contain all items that are relevant for your team, closed, in progress, and not started. Check out the [JQL reference](https://www.atlassian.com/blog/jira/jql-the-most-flexible-way-to-search-jira-14) if you need support.             | `issuetype in (\"Story\", \"Bug\") AND project = \"YourProject\" AND labels = \"YourTeamLabel\"`            |
| estimationField           | Which field is holding the estimates. This might be a custom field, depending on your process.            | *timetracking.originalEstimate*             |
| anonymizeLabel           | Anonymizes the labels in the charts, by not using the full issue key, but just the numbers.            | true or false             |

{: .note}
If you are using Jira Data Center, you must leave the *username* empty, as the authentication method differs from the one against Jira Cloud. Instead of an *API Token*, you must create a [Personal Access Token](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html) and specify this for the *apiToken* parameter.

{: .important}
If you want to use custom fields, you have to figure out the name of this customfield. This is some auto-generated number (for example *1232324*). If this custom field holds your estimate, you would need to specify the value: *customfield_1232324*.
Check the [Atlassion Documentation](https://confluence.atlassian.com/jirakb/find-my-custom-field-id-number-in-jira-744522503.html) to find out how to get the id of your custom field.

## Azure DevOps
In order use `flowpulse` with Azure DevOps, you must specify against which Azure DevOps organization you are working. For this you need a url, as well as a [Personal Access Token](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows). Furthermore you have to specify a query that gets the items of the team(s) you are interested in as well as how many days into the past you are interested in. Last but not least, you can specify which field you are using for estimates. The queries are written in [WIQL](https://learn.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops).


| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| organizationUrl           | The url to your Azure DevOps Organization. Replace _YourOrg_ with your actual organization name.               | https://dev.azure.com/YourOrg             |
| apiToken              | [Personal Access Token](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&tabs=Windows) to access the data in your organization             | ""              |
| itemQuery           | The query to get your teams items. Note that this should contain all items that are relevant for your team, closed, in progress, and not started. Check out the [WIQL reference](https://learn.microsoft.com/en-us/azure/devops/boards/queries/wiql-syntax?view=azure-devops) if you need support.             | ([System.WorkItemType] = \"User Story\" or [System.WorkItemType] = \"Bug\") AND [System.TeamProject] == \"Your Project\" AND [System.AreaPath] UNDER \"Team Project\\\\Team Name\"             |
| estimationField           | Which field is holding the estimates. You can see the "reference Name" for the fields if you browse to *https://dev.azure.com/%7Borganization%7D/%7Bproject%7D/_apis/wit/fields?api-version=7.1-preview.3* - and insert your organization and project            | Microsoft.VSTS.Scheduling.StoryPoints             |

{: note}
Check the [Azure DevOps Documentation](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/guidance/work-item-field?view=azure-devops) for a list of *Reference Names* for various fields.

# Charts
There are various *types* of charts. In the *charts* section, you can add all the chart types you want to generate. If you don't want a specific chart type, just delete the whole block from the config.

{: .note}
You can also generate the same chart type multiple times with different settings, just add multiple blocks of the type you want in the config (and don't forget to name it differently).

{: .recommendation}
This section is just about how to configure the various charts. If you want more details about the Charts, check out the [dedicated page](../charts/charts.html).

Every type of chart has different configuration settings. Read on to learn about the specifics.

## Cycle Time Scatter Plot
You can configure which percentiles you want to show for your Cycle Time Scatterplot, as well the coloring of those percentiles. You can find the color names in the documentation of [matplotlib](https://matplotlib.org/stable/gallery/color/named_colors.html#css-colors).

You can chose to specify a *trend line* as well, by passing *trend_settings*. If enabled, it will look back at the last x days (*window size*), and draw what the *percentile* was over this time. This would allow you to see how the trend evolves over time. You can remove the trend by deleting the whole line.

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| type           | The type of the chart               | "cycleTimeScatterPlot"             |
| chartName           | Name of the generated chart file               | "CycleTime.png"             |
| percentiles           | Array of percentile lines to show               | [50, 70, 85, 95]             |
| percentileColors           | Array of colors for the percentile lines               | ["red", "orange", "lightgreen", "darkgreen"]             |
| trend_settings           | Array containing [percentile, window size, color] for trend line               | [70, 10, "purple"]             |

## Work Item Age Scatter Plot
To visulize the Work Item Age, you can specify the *xAxisLines*. Use them to indicate when the items near your [Service Level Expectation](https://kanbanguides.org/english/), for example based on your 50th and 85th percentile of your Cycle Time. As in the [Cycle Time Scatterplot](#cycle-time-scatter-plot), you can define the colors of the lines via the *xAxisColors*.

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| type           | The type of the chart               | "workItemAgeScatterPlot"             |
| chartName           | Name of the generated chart file               | "WorkItemAge.png"             |
| xAxisLines           | Array of day values to show vertical lines               | [5, 10]             |
| xAxisLineColors           | Array of colors for the vertical lines               | ["orange", "red"]             |

## Throughput Run Chart
The only configuration parameter of the Throughput Run Chart is the unit of time. You can choose to group it by *days*, *weeks*, or *months*.

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| type           | The type of the chart               | "throughputRunChart"             |
| unit           | Time unit for grouping             | "days", "weeks", "months"             |
| chartName           | Name of the generated chart file               | "Throughput.png"             |

## Work In Process Run Chart
The Work In Process Run Chart (often also referred to as *Work in Progress Run Chart*) has no specific configuration option apart from the name.

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| type           | The type of the chart               | "workInProcessRunChart"             |
| chartName           | Name of the generated chart file               | "WorkInProcess.png"             |

## Started vs Finished Chart
The *Started vs Finished Chart* allows you to specify colors for visualizing *started* and *finished*. See [Cycle Time Scatterplot](#cycle-time-scatter-plot) for details on how to set colors.

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| type           | The type of the chart               | "startedVsFinishedChart"             |
| chartName           | Name of the generated chart file               | "StartedVsFinished.png"             |
| startedColor           | Color for started items line               | "orange"             |
| closedColor           | Color for finished items line               | "green"             |

## Estimation vs Cycle Time
The *Estimation vs Cycle Time* chart allows to configure the *unit* of your estimation. For example you can adjust it to *Man Days* or *Ideal Hours* or whatever kind of estimation you use.

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| type           | The type of the chart               | "estimationVsCycleTime"             |
| chartName           | Name of the generated chart file               | "EstimationVsCycleTime.png"             |
| estimationUnit           | Unit label for the estimation values               | "Story Points"             |

## Process Behaviour Charts
The *Process Behaviour Charts* will produce PBCs for all four flow metrics. Specify the start and end of your PBC baseline as dates in the format *YYYY-MM-dd*. The chart will show all the items from your [history](#general), whereas the baseline may be outside of your history.

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| type           | The type of the chart               | "processBehaviourCharts"             |
| baselineStart           | Start date for baseline period               | "2024-01-01"             |
| baselineEnd           | End date for baseline period               | "2024-01-31"             |
| throughputChartName           | Name for the throughput chart file               | "Throughput_PBC.png"             |
| cycleTimeChartName           | Name for the cycle time chart file               | "CycleTime_PBC.png"             |
| wipChartName           | Name for the WIP chart file               | "WorkInProgress_PBC.png"             |
| itemAgeChartName           | Name for the item age chart file               | "WorkItemAge_PBC.png"             |

# Forecasts
There are two *types* of forecasts, which are defined by their configuration:
- *How Many* forecasts that will tell you how many items can be done until a specific date
- *When* forecasts that will tell you when you will manage to finish a specific number of items

{: .recommendation}
This section is just about how to configure the forecasts. If you want more details about the Forecasts, check out the [dedicated page](../forecasts/forecasts.html).

{: .note}
In the *forecasts* section, you can add as many forecasts as you want to run. If you don't want to run any forecasts, just delete the whole block from the config.

FlowPulse will determine what kind of forecast to run based on the configuration values:

| Name                   | Description                          | Sample Value      |
|------------------------|--------------------------------------|--------------------|
| name           | The name of your Forecast.               | "Release 23.44" or "Sprint Goal"             |
| remainingBacklogQuery           | The query to get the remaining items for your forecast. Note that this should contain all items that are relevant for your forecast, so most likely you want to filter out closed and removed items. This is either a JQL query if you are using Jira or a WIQL query in the case of Azure DevOps.           | issuetype in (\"Story\", \"Bug\") AND project = \"YourProject\" AND status not in (\"Done\") AND fixVersion = \"Release 24.10\" |
| targetDate           | Either the date in *YYYY-mm-dd* format or the number of days in future               | "2024-10-31" / 14             |


## When
If you specify a *remainingBacklogQuery*, a *When* forecast will be executed with all items will be returned by this query. See [Jira](#jira) and [Azure DevOps](#azure-devops) for details on the query.

{: .important}
If you are using a CSV datasource, you cannot use a *query*, as it's not supported. Instead, it will use **all** items that are not yet closed. To run a *When* forecast, just add *true*, and if you want to skip the *When*, leave it empty: *""*

## How Many
If you want to run a *How Many* forecast, specify a *targetDate*. The target date is specified either as a date in the format *YYYY-MM-dd* or as number.
If you specify a number, it will use the date that is this amount of days in the future. For example *14* would mean it's 2 weeks in the future.

If you don't provide a *target date*, no "How Many" simulation will be run.

## When And How Many
If you provide both a *remainingBacklogQuery* and a *targetDate*, both forecast types will be run. In this case, you will also get the likelihood of closing all remaining items till the specified target date.