---
title: Forecasts
parent: Overview
layout: home
nav_order: 5
---

Forecasts are one of the two main features of FlowPulse. It's using [Monte Carlo Simulations](https://blog.letpeople.work/p/an-introduction-and-step-by-step-guide-to-monte-carlo-simulations) to make *How Many* and *When* forecasts.

{: .definition}
If you want to try out the tool with demo data, check out our [DemoConfig.json](../assets/exampledata/DemoConfig.json) and [DemoFile.csv](../assets/exampledata/DemoFile.csv). Download them, put them in the same directory, and run FlowPulse. It should generate **exactly** the same forecasts as you can see here.

- TOC
{:toc}

# Throughput and Predictability
The forecast will use your *Throughput* as input. This means it's using all items that were closed in the specified history. The more *continuous* your Throughput is (meaning the more equally distributed across this history), the more accurate the result will be. You can inspect this with the [Throughput Run Chart](../charts/charts.html#throughput-run-chart) and the [Process Behaviour Charts](../charts/charts.html#process-behaviour-charts).

A more *uneven* Throughput (for example by having 1.5 weeks of no items closed, and then many items within 2 days) will lead to more extreme results. That means, the optimistic forecast will be very optimisitc, while the pessimistic one will be very pessimistic. If the *distance* between the percentiles gets too big, the forecasts eventually will become useless. Take this example:

> There is a 50% chance to be done within 1 month, and an 85% chance that it will take 9 months or less

As the range is so wide, it's doubtful this is of any use. You can still run the forecasts like this, and they are *working*, it's just that they are as accurate as their input data. Predictability is something you do, and in the case of Forecasts using Monte Carlo Simulation it means you must take care of your flow (by looking at the Flow Metrics) to get useful results.

# How Many
How many can be useful for a planning event (for example a Sprint Planning). In FlowPulse, simply specify the *targetDate* and run it:

```bash
----------------------------------------------------------------  
Running Forecast for Sprint Forecast  
--------------------------------  
Running Monte Carlo Simulation - How Many items will be done till 2025-03-07  
--------------------------------  
50 Percentile: 12 Items  
70 Percentile: 10 Items  
85 Percentile: 7 Items  
95 Percentile: 5 Items  
----------------------------------------------------------------
```

In the above example we set the *targetDate* to *14*. This means it will automatically look 14 days ahead. This is nice to be able to re-run the forecasts for a fixed time period.

You can also specify a fixed Date as *targetDate*, this is useful for certain milestones that are not moving.

# When
To run a *When* forecast, you have to specify the *remainingItems*. Using this, you can specifcy all remaining items for your forecasts or they are fetched from your data srouce via query (be aware of the [limitations of this when using a CSV file](../configuration/configuration.html#when)) and it will tell you *When* all those items are expected to be done. This is great if you have a fixed set of items remaining (examples could include all items tagged for a specific Release, or that are needed for your Sprint Goal) and want to know when this is done.

```bash
----------------------------------------------------------------
Running Forecast for Next Release
--------------------------------
Running Monte Carlo Simulation - How Many items will be done till 2025-06-21
--------------------------------
50 Percentile: 107 Items
70 Percentile: 100 Items
85 Percentile: 92 Items
95 Percentile: 84 Items

Loading Items from CSV File: 'DemoFile.csv'. Started Date Column Name 'started_date', Closed Date Column Name 'closed_date', Start Date Format '%d.%m.%Y', and Closed Date Format '%d.%m.%Y'
Items Query not supported for CSV - Loading all items that are NOT closed
Found 121 Items in the CSV
--------------------------------
Running Monte Carlo Simulation - When will 121 items be done
--------------------------------
120 days to target date
50 Percentile: 135 days - Predicted Date: 2025-07-06
70 Percentile: 144 days - Predicted Date: 2025-07-15
85 Percentile: 154 days - Predicted Date: 2025-07-25
95 Percentile: 166 days - Predicted Date: 2025-08-06
Chance of hitting target date: 19.97
----------------------------------------------------------------
```

In the above example you also see that a forecast can have both, the *remainingItems* and the *targetDate* specified. In such a case, it's running both a *How Many* and *When* forecast, leading to giving you a probability of how likely it is to hit your target with the currently remaining items.

{: .note}
Right now, the output of the forecast is only visible in the terminal. If you need some other output (for example in a file) to process it further, please reach out to us via Slack.