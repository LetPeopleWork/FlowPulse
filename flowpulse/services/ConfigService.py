import os
import sys
import shutil
import json

from datetime import datetime, timedelta

SEPARATOR_LINE = "=" * 64


class ConfigService:

    def __init__(self):
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get_config_files(self):
        config_paths = [arg for arg in sys.argv[1:] if arg.lower().endswith(".json")]

        if len(config_paths) < 1:
            print(
                "No config files specified as arguments - trying to detect files in same directory"
            )
            config_paths.extend([f for f in os.listdir(os.getcwd()) if f.lower().endswith(".json")])

            if len(config_paths) < 1:
                print("No config file specified - copying defaults and using them")
                self.copy_default_config()
                config_paths.append("ExampleConfig.json")

        print("Using following configuration files: {0}".format(config_paths))
        return config_paths

    def copy_default_config(self):
        default_config_file = os.path.join(self.script_dir, "ExampleConfig.json")

        config_file_destination = os.path.join(os.getcwd(), os.path.basename(default_config_file))
        if not self.check_if_file_exists(config_file_destination):
            shutil.copy(default_config_file, config_file_destination)

    def check_if_file_exists(self, file_path, raise_if_not_found=False):
        if not os.path.isfile(file_path):
            if raise_if_not_found:
                raise FileNotFoundError(f"The file '{file_path}' does not exist.")

            return False

        return True

    def read_config(self, file_path):
        try:
            print("Reading Config File from {0}".format(file_path))

            self.check_if_file_exists(file_path, True)

            with open(file_path, "r") as file:
                config_data = json.load(file)
            return config_data
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error reading config file: {0}".format(file_path))
            raise

    def get_today(self, config):
        today = datetime.today()

        today_argument = config["general"].get("today", False)

        if today_argument:
            today = datetime.strptime(today_argument, "%Y-%m-%d")

        return today

    def get_history(self, config, today):
        history = config["general"].get("history", False)
        if not history:
            history = 90

            print("=== Warning ===")
            print("No history specified in the configuration file")
            print("Using default value of 90 days")
            print(SEPARATOR_LINE)

        return self.parse_history(history, today)

    def parse_history(self, history, today):
        try:
            history = int(history)
            print("Use rolling history of the last {0} days".format(history))
        except ValueError:
            history_start = datetime.strptime(history, "%Y-%m-%d")
            history = (today - history_start).days
            print(
                "Using history with fixed start date {0} - History is {1} days".format(
                    history_start, history
                )
            )

        return history

    def get_raw_data_csv_path(self, config):
        return config["general"].get("rawDataCsvPath", None)

    def get_data_source(self, config):
        data_source = config["general"].get("datasource", "")
        return data_source.lower().replace(" ", "")

    def get_data_sources(self, config):
        return config.get("dataSources", [])

    def get_show_plots(self, config):
        return config["general"].get("showPlots", False)

    def get_charts_folder(self, config):
        return config["general"].get("chartsFolder", "Charts")

    def get_plot_labels(self, config):
        return config["general"].get("plotLabels", True)

    def get_forecasts(self, config):
        return config.get("forecasts", [])

    def get_remaining_backlog_query(self, forecast_config):
        return forecast_config.get("remainingBacklogQuery", None)

    def get_target_date(self, forecast_config, today):
        target_date = forecast_config.get("targetDate", None)

        if target_date:
            if isinstance(target_date, int):
                target_date = (today + timedelta(target_date)).date()
            else:
                target_date = datetime.strptime(target_date, "%Y-%m-%d").date()

        return target_date

    def get_charts(self, config):
        return config.get("charts", [])

    def get_chart_type(self, chart_config):
        return chart_config.get("type", None)

    def get_trend_settings(self, chart_config):
        return chart_config.get("trend_settings", None)

    def get_pbc_baseline_dates(self, pbc_chart_config):
        baseline_start = datetime.strptime(pbc_chart_config["baselineStart"], "%Y-%m-%d")
        baseline_end = datetime.strptime(pbc_chart_config["baselineEnd"], "%Y-%m-%d")

        return baseline_start, baseline_end
