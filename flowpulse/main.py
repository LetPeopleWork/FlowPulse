import argparse
import os
import shutil
import json
import csv

import requests
from importlib.metadata import version

from datetime import datetime, timedelta

from FlowMetricsCSV.FlowMetricsService import FlowMetricsService
from MonteCarloCSV.MonteCarloService import MonteCarloService

from .JiraWorkItemService import JiraWorkItemService
from .AzureDevOpsWorkItemService import AzureDevOpsWorkItemService

def print_logo():
    logo = r"""
    /$$                 /$$           /$$$$$$$                           /$$                /$$      /$$                  /$$      
    | $$                | $$          | $$__  $$                         | $$               | $$  /$ | $$                 | $$      
    | $$       /$$$$$$ /$$$$$$        | $$  \ $$/$$$$$$  /$$$$$$  /$$$$$$| $$ /$$$$$$       | $$ /$$$| $$ /$$$$$$  /$$$$$$| $$   /$$
    | $$      /$$__  $|_  $$_/        | $$$$$$$/$$__  $$/$$__  $$/$$__  $| $$/$$__  $$      | $$/$$ $$ $$/$$__  $$/$$__  $| $$  /$$/
    | $$     | $$$$$$$$ | $$          | $$____| $$$$$$$| $$  \ $| $$  \ $| $| $$$$$$$$      | $$$$_  $$$| $$  \ $| $$  \__| $$$$$$/ 
    | $$     | $$_____/ | $$ /$$      | $$    | $$_____| $$  | $| $$  | $| $| $$_____/      | $$$/ \  $$| $$  | $| $$     | $$_  $$ 
    | $$$$$$$|  $$$$$$$ |  $$$$/      | $$    |  $$$$$$|  $$$$$$| $$$$$$$| $|  $$$$$$$      | $$/   \  $|  $$$$$$| $$     | $$ \  $$
    |________/\_______/  \___/        |__/     \_______/\______/| $$____/|__/\_______/      |__/     \__/\______/|__/     |__/  \__/
                                                                | $$                                                                
                                                                | $$                                                                
                                                                |__/                                                                
    """
    print(logo)
    
def check_for_updates(package_name):
    try:
        current_version = version(package_name)

        # Query PyPI for the latest version
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]

        # Compare versions
        if current_version != latest_version:
            print("------- Update Available -----------")
            print(f"Update available: {latest_version} (current: {current_version})")
            print(f"Run the following command to upgrade: 'python -m pip install --upgrade {package_name}'")
            print("------- Update Available -----------")

    except Exception:
        print("Error checking for updates - ignoring")


def copy_default_config(script_dir):        
    default_config_file = os.path.join(script_dir, "ExampleConfig.json")
    
    config_file_destination = os.path.join(os.getcwd(), os.path.basename(default_config_file))        
    if not check_if_file_exists(config_file_destination):
        shutil.copy(default_config_file, config_file_destination)

def check_if_file_exists(file_path, raise_if_not_found = False):
    if not os.path.isfile(file_path):
        if raise_if_not_found:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        
        return False
    
    return True

def read_config(file_path):
    print("Reading Config File from {0}".format(file_path))
    
    check_if_file_exists(file_path, True)
    
    with open(file_path, 'r') as file:
        config_data = json.load(file)
    return config_data

def main():
    try:
        print_logo()
        
        package_name = "flowpulse"
        current_version = version(package_name)
        
        print("================================================================")
        print("{0}@{1}".format(package_name, current_version))
        print("================================================================")  

        
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        parser = argparse.ArgumentParser()
        parser.add_argument("--ConfigFileNames", type=str, nargs='+', default=[])

        args = parser.parse_args()
        
        config_paths = args.ConfigFileNames
        
        if len(config_paths) < 1:
            print("No config file specified, copying defaults and using them")
            copy_default_config(script_dir)
            config_paths.append("ExampleConfig.json")
        
        print("Using following configuration files: {0}".format(config_paths))

        for config_path in config_paths:
            print("================================================================")
            config = read_config(config_path)
            
            # General Config
            show_plots = config["general"]["showPlots"]
            charts_folder = config["general"]["chartsFolder"]
                        
            today = datetime.today()
            try:
                today_argument = config["general"]["today"]
                
                if today_argument:
                    today = datetime.strptime(today_argument, "%Y-%m-%d")
            except:
                # No override for todays date
                print("No override for today")
            
            work_tracking_system = config["general"]["workTrackingSystem"]
            
            if work_tracking_system == "Jira":            
                print("Using Jira")
                jira_url = config["jira"]["url"]
                username = config["jira"]["username"]
                api_token = config["jira"]["apiToken"]
                item_query = config["jira"]["itemQuery"]
                estimation_field = config["jira"]["estimationField"]
                
                try:
                    anonymize_label = config["jira"]["anonymizeLabel"]
                except:
                    anonymize_label = False
                
                history_in_days = parse_history_argument("jira", config, today)
            
                work_item_service = JiraWorkItemService(jira_url, username, api_token, estimation_field, history_in_days, anonymize_label)
            elif work_tracking_system == "Azure DevOps":
                print("Using Azure DevOps")
                org_url = config["azureDevOps"]["organizationUrl"]
                api_token = config["azureDevOps"]["apiToken"]
                item_query = config["azureDevOps"]["itemQuery"]
                estimation_field = config["azureDevOps"]["estimationField"]
                
                history_in_days = parse_history_argument("azureDevOps", config, today)
                
                work_item_service = AzureDevOpsWorkItemService(org_url, api_token, estimation_field, history_in_days = parse_history_argument("jira", config, today))
            else:
                raise Exception("Work Tracking System {0} not supported. Supported values are 'Jira' and 'Azure DevOps'".format(work_tracking_system))
            
            work_items = work_item_service.get_items_via_query(item_query)
            work_items = [item for item in work_items if item.started_date is not None]     
            
            flow_metrics_service = FlowMetricsService(show_plots, charts_folder, today)            
            write_workitems_to_csv(config, work_items, charts_folder)           
            
            print("Creating Charts as per the configuration...")
            print("----------------------------------------------------------------")   
            
            if len(work_items) < 1:
                print("No items - skipping")
                exit()
                
            def run_forecasts():
                forecasts = config["forecasts"]
                
                monte_carlo_service = MonteCarloService(history_in_days, today.date(), False)
                
                closed_items = [item for item in work_items if item.closed_date is not None]
                
                if len(closed_items) == 0:
                    print("No closed items found with specified configuration - skipping forecasts")
                    return
                
                throughput_history = monte_carlo_service.create_closed_items_history(closed_items)
                
                for forecast in forecasts:                    
                    print("Running Forecast for {0}".format(forecast["name"]))
                    
                    run_mc_when = False
                    run_mc_how_many = False
                    
                    if "remainingBacklogQuery" in forecast:
                        remaining_items_query = forecast["remainingBacklogQuery"]
                        run_mc_when = True
                    
                    if "targetDate" in forecast:    
                        target_date = forecast["targetDate"]
                        run_mc_how_many = True
                    
                    if target_date:
                        if isinstance(target_date, int):
                            target_date = (today + timedelta(target_date)).date()
                        else:
                            target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                    else:
                        target_date = None
                        run_mc_how_many = False
                    
                    if run_mc_how_many:
                        monte_carlo_service.how_many(target_date, throughput_history)
                    
                    if run_mc_when:
                        remaining_items = work_item_service.get_items_via_query(remaining_items_query)
                        monte_carlo_service.when(len(remaining_items), throughput_history, target_date)

            def create_cycle_time_scatterplot():
                chart_config = config["cycleTimeScatterPlot"]
                
                trend_settings = None
                if "trend_settings" in chart_config:
                    trend_settings = chart_config["trend_settings"]

                if chart_config["generate"]:
                    history = parse_history(chart_config["history"], today)
                    flow_metrics_service.plot_cycle_time_scatterplot(work_items, history, chart_config["percentiles"], chart_config["percentileColors"], chart_config["chartName"], trend_settings)

            def create_work_item_age_scatterplot():
                chart_config = config["workItemAgeScatterPlot"]

                if chart_config["generate"]:
                    history = parse_history(chart_config["history"], today)
                    flow_metrics_service.plot_work_item_age_scatterplot(work_items, history, chart_config["xAxisLines"], chart_config["xAxisLineColors"], chart_config["chartName"])

            def create_throughput_run_chart():
                chart_config = config["throughputRunChart"]

                if chart_config["generate"]:
                    history = parse_history(chart_config["history"], today)
                    flow_metrics_service.plot_throughput_run_chart(work_items, history, chart_config["chartName"], chart_config["unit"])            

            def create_work_in_process_run_chart():
                chart_config = config["workInProcessRunChart"]

                if chart_config["generate"]:
                    history = parse_history(chart_config["history"], today)
                    flow_metrics_service.plot_work_in_process_run_chart(work_items, history, chart_config["chartName"])

            def create_work_started_vs_finished_chart():
                chart_config = config["startedVsFinishedChart"]

                if chart_config["generate"]:
                    history = parse_history(chart_config["history"], today)
                    flow_metrics_service.plot_work_started_vs_finished_chart(work_items, history, chart_config["startedColor"], chart_config["closedColor"], chart_config["chartName"])

            def create_estimation_vs_cycle_time_chart():
                chart_config = config["estimationVsCycleTime"]

                if chart_config["generate"]:
                    history = parse_history(chart_config["history"], today)
                    flow_metrics_service.plot_estimation_vs_cycle_time_scatterplot(work_items, history, chart_config["chartName"], chart_config["estimationUnit"])

            def create_process_behaviour_charts():
                chart_config = config["processBehaviourCharts"]

                if chart_config["generate"]:
                    history = parse_history(chart_config["history"], today)
                    baseline_start = datetime.strptime(chart_config["baselineStart"], "%Y-%m-%d")
                    baseline_end = datetime.strptime(chart_config["baselineEnd"], "%Y-%m-%d")

                    flow_metrics_service.plot_throughput_process_behaviour_chart(work_items, baseline_start, baseline_end, history, chart_config["throughputChartName"])            
                    flow_metrics_service.plot_wip_process_behaviour_chart(work_items, baseline_start, baseline_end, history, chart_config["wipChartName"])
                    flow_metrics_service.plot_cycle_time_process_behaviour_chart(work_items, baseline_start, baseline_end, history, chart_config["cycleTimeChartName"])       
                    flow_metrics_service.plot_total_age_process_behaviour_chart(work_items, baseline_start, baseline_end, history, chart_config["itemAgeChartName"])                        

            print("---------------------------")
            print("Creating Charts...")
            create_cycle_time_scatterplot()
            create_work_item_age_scatterplot()
            create_throughput_run_chart()
            create_work_in_process_run_chart()
            create_work_started_vs_finished_chart()
            create_estimation_vs_cycle_time_chart()    
            create_process_behaviour_charts()       
            
            print("---------------------------")
            print("Running Forecasts")
            run_forecasts()

            print()
            check_for_updates(package_name)
            print()
            print("🛈 Want to learn more about how all of this works? Check out our website! 🛈")
            print("🔗 https://letpeople.work 🔗")
    except Exception as exception:
        print("Error while executing flowpulse:")
        print(exception)
        
        print("🪲 If the problem cannot be solved, consider opening an issue on GitHub: https://github.com/LetPeopleWork/flowpulse/issues 🪲")

def parse_history_argument(work_tracking_system, config, today):
    try:
        history = config[work_tracking_system]["history"]
    except:
        # Backward compatibility for using old parameter name
        history = int(config[work_tracking_system]["historyInDays"])
        
        print("=== Warning ===")
        print("You are using the old parameter 'historyInDays' - please switch to the new name 'history'")
        print("=============")
        
    return parse_history(history, today)

def write_workitems_to_csv(config, work_items, charts_folder):
    try:
        csv_file_name = config["general"]["rawDataCSV"]
    except:
        csv_file_name = ""
        
    if csv_file_name:
        csv_file_path = os.path.join(charts_folder, csv_file_name)
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            
            writer.writerow([
                'id', 'title', 'estimation', 'started_date', 'closed_date', 
                'work_item_age', 'cycle_time', 'state_changed_date'
            ])
        
            for item in work_items:
                row = [
                    str(item.id),
                    str(item.title),
                    str(item.estimation),
                    item.started_date.date().isoformat() if item.started_date else "",
                    item.closed_date.date().isoformat() if item.closed_date else "",
                    str(item.work_item_age) if item.work_item_age is not None else "",
                    str(item.cycle_time) if item.cycle_time is not None else "",
                    item.started_date.date().isoformat() if item.started_date else "",
                ]
                
                writer.writerow(row)
        
        print(f"Work items exported to {csv_file_path}")

def parse_history(history, today):
    try:
        history = int(history)
        print("Use rolling history of the last {0} days".format(history))
    except ValueError:
        history_start = datetime.strptime(history, "%Y-%m-%d").date()
        history = (today - history_start).days
        print("Using history with fixed start date {0} - History is {1} days".format(history_start, history))
            
    return history

if __name__ == "__main__":    
    main()