---
title: Installation
parent: Overview
layout: home
nav_order: 1
---

This section will hopefully tell you everything you need to know to install, run, and update FlowPulse.

- TOC
{:toc}


# Prerequisites
Make sure you have Python 3.10 or higher installed on your system. You can check your Python version by opening a terminal and running:

```bash
python --version
```

If this shows Python 3.10 or higher, you're good to go. If not, or if you get an error, download and install the latest Python version from the [official Python Website](https://www.python.org/downloads/). During installation, make sure to check the option "Add Python to PATH" to make Python available from your terminal.

{: .note}
It can be that you have to use `python3 --version`. If this is the case, please use always `python3` instead of `python` in the following commands.

# Installation
FlowPulse is written in Python, and available as a published package on [PyPi](https://pypi.org/).

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
Open a terminal of your choice, simply type in `flowpulse`, and flowpulse will be run using a *default configuration*. See more on that [below](#specifying-configuration-files)

## From Source
If you run it from the source code, navigate to the folder where you stored the source and open a terminal at this location. Then run the following command:

```bash
python -m flowpulse.main
```

# Specifying Configuration Files
The tool needs to know what to run:
- Where to get the input data from?
- What charts to create?
- What forecasts to run?

This is done via a configuration file. You can find all about this under [Configuration](../configuration/configuration.html).

Following is a description of how you can specify which configuration to use.

## Example Configuration
If no configuration is available, FlowPulse will automatically create an `ExampleConfig.json` in your current directory and use this. The default [Data Source](../datasource/datasources.html) will be CSV, and *FlowPulse* will create a default CSV file and create some charts for you.

{: .recommended}
It's recommended to rename your config file from *ExampleConfig.json* to something more meaningful (like *TeamNameConfig.json*) and to specify this configuration file when running it again: `flowpulse "TeamNameConfig.json"`.

## Automatic Configuration Discovery
flowpulse will scan the directory you start it from for *json* files. Every *.json* will be treated as FlowPulse configuration and is automatically loaded. This means, if you have a *FlowPulse* directory that has the following files:

```bash
- FlowPulse/
    - TeamA_Config.json
    - TeamB_Config.json
    - TeamC_Config.json
```

You can simply run the tool from the *FlowPulse* directory and it will execute for every of those 3 configuration:

    /FlowPulse>FlowPulse

    No config files specified as arguments - trying to detect files in same directory
    Using following configuration files: ['TeamA_Config.json', 'TeamB_Config.json', 'TeamC_Config.json']
    ================================================================
    Running flowpulse for config file: TeamA_Config.json
    ================================================================
    Reading Config File from TeamA_Config.json
    ...

## Specify Configuration File
You can also start FlowPulse and specify which configuration file exactly you want to run, by putting the relative or absolute path after the startup parameters:

```bash
flowpulse "TeamA_Config.json"

flowpulse "C:\Data\FlowPulse\ExampleConfig.json"
```

You can also multiple configurations that you can use to create different charts and/or run different forecasts. For example for different teams or different item types (for example if you want to visualize Epics differently than other work items).
Each configuration is independent and can work against different input files. If you want to generate many charts/forecasts at once with different configurations, you can also specify multiple configuration files:  
```bash
flowpulse "TeamA_Config.json" "TeamB_Config.json" "TeamC_Config.json"
```

This will generate you three sets of charts as per the individual configurations specified.

{: .note}
Make sure to specify different folders or chart names in the respective configs, as otherwise they will be overwritten.

Check [Configuration](../configuration/configuration.html) to see all details on how to configure  FlowPulse.

# Updating FlowPulse
We try to update FlowPulse as often as needed. So you will sooner or later need to update it.

FlowPulse is displaying a message if it detects that a newer version is available
```bash
------- Update Available -----------
Update available: 1.1.11 (current: 1.1.8)
Run the following command to upgrade: 'python -m pip install --upgrade flowpulse'
------- Update Available -----------
```

## Python Package
All you need to do to update FlowPulse is run the update command:
```bash
python -m pip install --upgrade flowpulse
```

That's it. Enjoy the latest version.

## From Source
There are two ways to update if you are running from source.

If you downloaded the files as zip, you can redownload the latest version, and overwrite the existing files.

If you cloned the repository, you can run:
```bash
git pull
```
And it should fetch the latest files from the GitHub Repository, assuming you have not changed any existing files (again, please refer to the Git and GitHub documentation if you are not familiar with it)

{: .note}
We recommend using the python package approach. But if you run it from source, we highly recommend to keep your config files in a separate location, not "next" to the code. That way, you can more easily download new versions, as it allows you to delete the old version and completely replace it with the new one, without fear of losing your configurations.