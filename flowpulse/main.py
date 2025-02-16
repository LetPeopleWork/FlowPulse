from .services.CsvService import CsvService
from .services.FlowMetricsService import FlowMetricsService
from .services.MonteCarloService import MonteCarloService
from .services.WorkItemServiceFactory import WorkItemServiceFactory
from .services.WorkItemFilterService import WorkItemFilterService
from .services.PackageService import PackageService
from .services.ConfigService import ConfigService

SEPARATOR_LINE = "=" * 64
SMALL_SEPERATOR_LINE = "-" * 64

package_service = PackageService()
config_service = ConfigService()
flow_metrics_service = None


def run_forecast(
    forecast_config, today, throughput_history, monte_carlo_service, work_item_service
):
    print(SMALL_SEPERATOR_LINE)
    print("Running Forecast for {0}".format(forecast_config["name"]))

    target_date = None
    run_mc_when = False
    run_mc_how_many = False

    remaining_items_query = config_service.get_remaining_backlog_query(forecast_config)
    target_date = config_service.get_target_date(forecast_config, today)

    if remaining_items_query:
        run_mc_when = True

    if target_date:
        run_mc_how_many = True

    if run_mc_how_many:
        monte_carlo_service.how_many(target_date, throughput_history)

    if run_mc_when:
        remaining_items = work_item_service.get_items(remaining_items_query)
        monte_carlo_service.when(len(remaining_items), throughput_history, target_date)


def create_forecasts(
    config,
    history,
    today,
    work_items,
    work_item_filter_service,
    work_item_service,
):
    print(SEPARATOR_LINE)
    print("Running Forecasts")
    print(SEPARATOR_LINE)

    forecasts = config_service.get_forecasts(config)
    closed_items = work_item_filter_service.get_closed_items(work_items)

    if len(closed_items) == 0:
        print("No closed items found with specified configuration - skipping forecasts")
        return

    monte_carlo_service = MonteCarloService(history, today.date(), False)
    throughput_history = monte_carlo_service.create_closed_items_history(closed_items)

    for forecast_config in forecasts:
        run_forecast(
            forecast_config, today, throughput_history, monte_carlo_service, work_item_service
        )


def create_chart(chart_config, work_items, flow_metrics_service):
    chart_type = config_service.get_chart_type(chart_config)
    print(SMALL_SEPERATOR_LINE)
    print(f"Creating chart: {chart_type}")

    match chart_type.lower():
        case "cycletimescatterplot":
            trend_settings = config_service.get_trend_settings(chart_config)
            flow_metrics_service.plot_cycle_time_scatterplot(
                work_items,
                chart_config["percentiles"],
                chart_config["percentileColors"],
                chart_config["chartName"],
                trend_settings,
            )
        case "workitemagescatterplot":
            flow_metrics_service.plot_work_item_age_scatterplot(
                work_items,
                chart_config["xAxisLines"],
                chart_config["xAxisLineColors"],
                chart_config["chartName"],
            )
        case "throughputrunchart":
            flow_metrics_service.plot_throughput_run_chart(
                work_items, chart_config["chartName"], chart_config["unit"]
            )
        case "workinprocessrunchart":
            flow_metrics_service.plot_work_in_process_run_chart(
                work_items, chart_config["chartName"]
            )
        case "startedvsfinishedchart":
            flow_metrics_service.plot_work_started_vs_finished_chart(
                work_items,
                chart_config["startedColor"],
                chart_config["closedColor"],
                chart_config["chartName"],
            )
        case "estimationvscycletime":
            flow_metrics_service.plot_estimation_vs_cycle_time_scatterplot(
                work_items, chart_config["chartName"], chart_config["estimationUnit"]
            )
        case "processbehaviourcharts":
            baseline_start, baseline_end = config_service.get_pbc_baseline_dates(chart_config)
            flow_metrics_service.plot_throughput_process_behaviour_chart(
                work_items, baseline_start, baseline_end, chart_config["throughputChartName"]
            )
            flow_metrics_service.plot_wip_process_behaviour_chart(
                work_items, baseline_start, baseline_end, chart_config["wipChartName"]
            )
            flow_metrics_service.plot_cycle_time_process_behaviour_chart(
                work_items, baseline_start, baseline_end, chart_config["cycleTimeChartName"]
            )
            flow_metrics_service.plot_total_age_process_behaviour_chart(
                work_items, baseline_start, baseline_end, chart_config["itemAgeChartName"]
            )

        case _:  # This is the default case
            print(f"Unknown chart type: {chart_type} - skipping")


def create_charts(config, today, history, work_items, work_item_filter_service):
    show_plots = config_service.get_show_plots(config)
    charts_folder = config_service.get_charts_folder(config)
    plot_labels = config_service.get_plot_labels(config)

    flow_metrics_service = FlowMetricsService(
        show_plots, charts_folder, work_item_filter_service, history, plot_labels, today
    )

    print(SEPARATOR_LINE)
    print("Creating Charts as per the configuration...")
    print(SEPARATOR_LINE)

    charts = config_service.get_charts(config)
    for chart_config in charts:
        create_chart(chart_config, work_items, flow_metrics_service)


def load_work_items(config, work_item_service):
    work_items = work_item_service.get_items()

    print("Creating Charts as per the configuration...")
    print("----------------------------------------------------------------")

    if len(work_items) < 1:
        print("No items - skipping")
        exit()

    raw_data_csv_path = config_service.get_raw_data_csv_path(config)
    if raw_data_csv_path:
        CsvService.write_workitems_to_csv(raw_data_csv_path, work_items)

    return work_items


def run_tool_for_config_file(config_path):
    print(SEPARATOR_LINE)
    print("Running flowpulse for config file: {0}".format(config_path))
    print(SEPARATOR_LINE)
    config = config_service.read_config(config_path)

    today = config_service.get_today(config)
    history = config_service.get_history(config, today)
    data_source = config_service.get_data_source(config)
    data_sources = config_service.get_data_sources(config)

    work_item_service = WorkItemServiceFactory().create_service(
        data_source, data_sources, history, today
    )
    work_items = load_work_items(config, work_item_service)

    work_item_filter_service = WorkItemFilterService(today, history)

    create_charts(config, today, history, work_items, work_item_filter_service)
    create_forecasts(
        config, history, today, work_items, work_item_filter_service, work_item_service
    )


def main():
    try:
        package_service.print_current_version()
        config_paths = config_service.get_config_files()

        for config_path in config_paths:
            run_tool_for_config_file(config_path)

        print()
        package_service.check_for_updates()
        print()
        print("🛈 Want to learn more about how all of this works? Check out our website! 🛈")
        print("🔗 https://letpeople.work 🔗")
    except Exception as exception:
        print("Error while executing flowpulse:")
        print(exception)

        print("🪲 If the problem cannot be solved, consider opening an issue on GitHub:")
        print("🔗 https://github.com/LetPeopleWork/flowpulse/issues 🪲")


if __name__ == "__main__":
    main()
