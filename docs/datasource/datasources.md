---
title: Data Sources
parent: Overview
layout: home
nav_order: 3
---

Right now, FlowPulse supports these data sources:

- TOC
{:toc}

Each of them comes with different configuration options. Check out the [Configuration](../../configuration/configuration.html) section for details on the configuration. This section will give you an overview over the specifics of each data source.

# CSV
CSV files are nice because almost any tool has some kind of export that will allow you to export it in this format. Check the [CSV Options](../configuration/configuration.html#csv) to see what fields you must provide for FlowPulse to work.

{: .recommendation}
We recommend to use a CSV file if you are just getting started. It's the most simple way to try out both forecasts and flow metrics. Even if you have Azure DevOps or Jira, it might be easier to get started with a CSV as the configuration is easier. You can try out the tool quickly and still move to the more advanced datasources later.

{: .definition}
If you want to try out the tool with demo data, check out our [DemoConfig.json](../assets/exampledata/DemoConfig.json) and [DemoFile.csv](../assets/exampledata/DemoFile.csv). Download them, put them in the same directory, and run FlowPulse.

# Jira
If you are using Jira and would not like to re-download a csv file every day/week to generate the new charts, you can also hook it up directly to your Jira.

{: .note}
While the automation is nice in general, you will also have less freedom. As you can highly customize a CSV file, certain things (for example the "started date") are automatically read from Jira. If for whatever reason you don't want to use the date that Jira thinks is the *correct* date, you might be better off with the CSV option.

If you use Jira as your data source, you can simply rerun the script with the same configuration, and it will automatically include the latest data, as it will run a *JQL* query to receive all information directly from Jira.

{: .recommendation}
This method works great if you start to use Flow Metrics and Forecasts on a daily or weekly basis. The true power of this only is unlocked if you do it **continuously**. It will make it easy to re-generate the charts and would also be suited to run as a scheduled job (for example within your pipelines).

We suggest to specify the *itemQuery* in a way that it does not get **all** the items, but you may want to filter for something like *updated after a certain date*, in order to speed up the data fetching.

{: .note}
We're not experts in JQL, so we will not be able to help you in writing you specific query. That said, please consider our [Slack Community](https://join.slack.com/t/let-people-work/shared_invite/zt-2y0zfim85-qhbgt8N0yw90G1P~JWXvlg) to get support from us and other users from FlowPulse.

# Azure DevOps
If you are using Azure DevOps and would not like to re-download a csv file every day/week to generate the new charts, you can also hook it up directly to your Azure DevOps.

{: .note}
While the automation is nice in general, you will also have less freedom. As you can highly customize a CSV file, certain things (for example the "started date") are automatically read from Azure DevOps. If for whatever reason you don't want to use the date that Azure DevOps thinks is the *correct* date, you might be better off with the CSV option.

If you use Azure DevOps as your data source, you can simply rerun the script with the same configuration, and it will automatically include the latest data, as it will run a *WIQL* query to receive all information directly from Azure DevOps.

{: .recommendation}
This method works great if you start to use Flow Metrics and Forecasts on a daily or weekly basis. The true power of this only is unlocked if you do it **continuously**. It will make it easy to re-generate the charts and would also be suited to run as a scheduled job (for example within your pipelines).

We suggest to specify the *itemQuery* in a way that it does not get **all** the items, but you may want to filter for something like *updated after a certain date*, in order to speed up the data fetching.

{: .note}
We're not experts in WIQL, so we will not be able to help you in writing you specific query. That said, please consider our [Slack Community](https://join.slack.com/t/let-people-work/shared_invite/zt-2y0zfim85-qhbgt8N0yw90G1P~JWXvlg) to get support from us and other users from FlowPulse.