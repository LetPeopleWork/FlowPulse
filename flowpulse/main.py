import os
import shutil
import json
import sys

import requests

SEPARATOR_LINE = "=" * 64

from importlib.metadata import version

from datetime import datetime, timedelta

from .services.CsvService import CsvService
from .services.FlowMetricsService import FlowMetricsService
from .services.MonteCarloService import MonteCarloService
from .services.WorkItemServiceFactory import WorkItemServiceFactory
from .services.WorkItemFilterService import WorkItemFilterService


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
        
        print(SEPARATOR_LINE)
        print("{0}@{1}".format(package_name, current_version))
        print(SEPARATOR_LINE)  

        
        script_dir = os.path.dirname(os.path.abspath(__file__))
                       
        config_paths = [arg for arg in sys.argv[1:] if arg.lower().endswith('.json')]
        
        if len(config_paths) < 1:
            print("No config files specified as arguments - trying to detect files in same directory")
            config_paths.extend([f for f in os.listdir(os.getcwd()) if f.lower().endswith('.json')])
            
            if len(config_paths) < 1:
                print("No config file specified - copying defaults and using them")
                copy_default_config(script_dir)
                config_paths.append("ExampleConfig.json")
        
        print("Using following configuration files: {0}".format(config_paths))

        for config_path in config_paths:
            print(SEPARATOR_LINE)
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
            
            history_in_days = parse_history_argument(config, today)
            plot_labels = config["general"].get("plotLabels", True)

            work_item_service = WorkItemServiceFactory().create_service(config, history_in_days, today)
            work_item_filter_service = WorkItemFilterService(today, history_in_days)
            flow_metrics_service = FlowMetricsService(show_plots, charts_folder, work_item_filter_service, history_in_days, plot_labels, today)     
            monte_carlo_service = MonteCarloService(history_in_days, today.date(), False)
            
            work_items = work_item_service.get_items()                   
            write_workitems_to_csv(config, work_items, charts_folder)           
            
            print("Creating Charts as per the configuration...")
            print("----------------------------------------------------------------")   
            
            if len(work_items) < 1:
                print("No items - skipping")
                exit()
                
            def run_forecasts():
                forecasts = config["forecasts"]               
                
                closed_items = work_item_filter_service.get_closed_items(work_items)
                
                if len(closed_items) == 0:
                    print("No closed items found with specified configuration - skipping forecasts")
                    return
                
                throughput_history = monte_carlo_service.create_closed_items_history(closed_items)
                
                for forecast in forecasts:                    
                    print("Running Forecast for {0}".format(forecast["name"]))
                    
                    target_date = None                    
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
                        remaining_items = work_item_service.get_items(remaining_items_query)
                        monte_carlo_service.when(len(remaining_items), throughput_history, target_date)

            def create_cycle_time_scatterplot():
                try:
                    chart_config = config["cycleTimeScatterPlot"]
                except KeyError:
                    return
                
                trend_settings = None
                if "trend_settings" in chart_config:
                    trend_settings = chart_config["trend_settings"]

                if chart_config["generate"]:
                    flow_metrics_service.plot_cycle_time_scatterplot(work_items, chart_config["percentiles"], chart_config["percentileColors"], chart_config["chartName"], trend_settings)

            def create_work_item_age_scatterplot():
                try:
                    chart_config = config["workItemAgeScatterPlot"]
                except KeyError:
                    return

                if chart_config["generate"]:
                    flow_metrics_service.plot_work_item_age_scatterplot(work_items, chart_config["xAxisLines"], chart_config["xAxisLineColors"], chart_config["chartName"])

            def create_throughput_run_chart():
                try:
                    chart_config = config["throughputRunChart"]
                except KeyError:
                    return

                if chart_config["generate"]:
                    flow_metrics_service.plot_throughput_run_chart(work_items, chart_config["chartName"], chart_config["unit"])            

            def create_work_in_process_run_chart():
                try:
                    chart_config = config["workInProcessRunChart"]
                except KeyError:
                    return

                if chart_config["generate"]:
                    flow_metrics_service.plot_work_in_process_run_chart(work_items, chart_config["chartName"])

            def create_work_started_vs_finished_chart():
                try:
                    chart_config = config["startedVsFinishedChart"]
                except KeyError:
                    return

                if chart_config["generate"]:
                    flow_metrics_service.plot_work_started_vs_finished_chart(work_items, chart_config["startedColor"], chart_config["closedColor"], chart_config["chartName"])

            def create_estimation_vs_cycle_time_chart():
                try:
                    chart_config = config["estimationVsCycleTime"]
                except KeyError:
                    return

                if chart_config["generate"]:
                    flow_metrics_service.plot_estimation_vs_cycle_time_scatterplot(work_items, chart_config["chartName"], chart_config["estimationUnit"])

            def create_process_behaviour_charts():
                try:
                    chart_config = config["processBehaviourCharts"]
                except KeyError:
                    return

                if chart_config["generate"]:
                    baseline_start = datetime.strptime(chart_config["baselineStart"], "%Y-%m-%d")
                    baseline_end = datetime.strptime(chart_config["baselineEnd"], "%Y-%m-%d")

                    flow_metrics_service.plot_throughput_process_behaviour_chart(work_items, baseline_start, baseline_end, history_in_days, chart_config["throughputChartName"])            
                    flow_metrics_service.plot_wip_process_behaviour_chart(work_items, baseline_start, baseline_end, history_in_days, chart_config["wipChartName"])
                    flow_metrics_service.plot_cycle_time_process_behaviour_chart(work_items, baseline_start, baseline_end, history_in_days, chart_config["cycleTimeChartName"])       
                    flow_metrics_service.plot_total_age_process_behaviour_chart(work_items, baseline_start, baseline_end, history_in_days, chart_config["itemAgeChartName"])                        

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

def parse_history_argument(config, today):
    try:
        history = config["general"]["history"]
    except:
        # Backward compatibility for using old parameter name
        history = 90
        
        print("=== Warning ===")
        print("You are using the old parameter 'historyInDays' - please switch to the new name 'history'")
        print("Using default value of 90 instead")
        print(SEPARATOR_LINE)
        
    return parse_history(history, today)

def parse_history(history, today):
    try:
        history = int(history)
        print("Use rolling history of the last {0} days".format(history))
    except ValueError:
        history_start = datetime.strptime(history, "%Y-%m-%d")
        history = (today - history_start).days
        print("Using history with fixed start date {0} - History is {1} days".format(history_start, history))
            
    return history

def write_workitems_to_csv(config, work_items, charts_folder):
    try:
        csv_file_name = config["general"]["rawDataCSV"]
    except:
        csv_file_name = ""
        
    if csv_file_name:
        CsvService.write_workitems_to_csv(csv_file_name, work_items, charts_folder)
        
if __name__ == "__main__":    
    main()