---
title: Installation
parent: Overview
layout: home
nav_order: 1
---

- TOC
{:toc}

# Installation
FlowPulse is written in Python, and available as a published package on [PyPi](https://pypi.org/).

## Prerequisites
Make sure you have Python 3.6 or higher installed on your system. You can check your Python version by opening a terminal and running:

```bash
python --version
```

If this shows Python 3.6 or higher, you're good to go. If not, or if you get an error, download and install the latest Python version from the [official Python Website](https://www.python.org/downloads/). During installation, make sure to check the option "Add Python to PATH" to make Python available from your terminal.

{: .note}
It can be that you have to use `python3 --version`. If this is the case, please use always `python3` instead of `python` in the following commands.

## Python Package
The best, and recommended way to install *FlowPulse* is via the Python Package Manager *pip*. Once you have made sure python is installed, you can download `flowpulse` via pip:
```bash
python -m pip install --upgrade flowpulse
```

If everything went well, you should see the following message in your terminal (the FlowPulse version should match the latest version available on [PyPi](https://pypi.org/project/flowpulse/)):
```bash
Successfully installed flowpulse-1.1.6
```

## From Source
If for some reason (for example some internal IT policy), you cannot install the package, you can also download the sources from [GitHub](https://github.com/letpeoplework/flowpulse).
Either just download the code as zip, or, if you are familiar with git, clone the repository.

{: .note}
If you need support on how to clone a repository, please check the [GitHub Documentation](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

# Running FlowPulse
Once you've installed FlowPulse, you can run it. Here's how.

## Python Package
Open a terminal of your choice, type in `flowpulse`, and something will happen. If no configuration is available, it will automatically create an `ExampleConfig.json` to your current directory and use this. The default [Data Source](../concepts/concepts.html) will be CSV, and *FlowPulse* will create a default CSV file and create some charts for you.

**Note**: It's recommended to rename your config file from *ExampleConfig.json* to something more meaningful (like *TeamNameConfig.json*) and to specify this configuration file when running it again: `flowpulse "TeamNameConfig.json"`.

## From Source
Bla Bla

### Running FlowPulse with multiple Configurations
You can have multiple configurations that you can use to create different charts and/or run different forecasts. For example for different teams or different item types (for example if you want to visualize Epics differently than other work items).
Each configuration is independent and can work against different input files. If you want to generate many charts/forecasts at once with different configurations, you can also specify multiple configuration files:
`flowpulse --ConfigFileNames "TeamA_Config.json" "TeamB_Config.json" "TeamC_Config.json"`

This will generate you three sets of charts as per the individual configurations specified.
**Note:** Make sure to specify different folders or chart names in the respective configs, as otherwise they will be overwritten.

Check [Configuration](../configuration/configuration.html) to see all details on how to configure  `flowpulse`.

# Updating FlowPulse


## Python Package

- note: indication of flowpulse

## From Source
- Redownload
- git pull