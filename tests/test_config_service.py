import pytest
import json
from datetime import datetime, timedelta
from flowpulse.services.ConfigService import ConfigService


@pytest.fixture
def config_service():
    return ConfigService()


@pytest.fixture
def sample_config():
    return {
        "general": {
            "today": "2023-12-01",
            "history": "90",
            "rawDataCsvPath": "data/raw.csv",
            "datasource": "Azure DevOps",
            "showPlots": True,
            "chartsFolder": "TestCharts",
            "plotLabels": True,
        },
        "dataSources": [
            {"name": "source1", "query": "query1"},
            {"name": "source2", "query": "query2"},
        ],
        "forecasts": [
            {"name": "forecast1", "remainingBacklogQuery": "query1", "targetDate": "2024-01-01"}
        ],
        "charts": [{"type": "burndown", "trendSettings": {"window": 14}}],
    }


@pytest.fixture
def temp_config_file(tmp_path, sample_config):
    config_file = tmp_path / "test_config.json"
    with open(config_file, "w") as f:
        json.dump(sample_config, f)
    return config_file


class TestConfigService:
    def test_get_today(self, config_service, sample_config):
        today = config_service.get_today(sample_config)
        assert today == datetime.strptime("2023-12-01", "%Y-%m-%d")

    def teset_get_today_not_set(self, config_service, sample_config):
        sample_config["general"].pop("today")
        today = config_service.get_today(sample_config)
        assert today == datetime.now().date()

    def test_get_history_with_days(self, config_service, sample_config):
        today = datetime.strptime("2023-12-01", "%Y-%m-%d")
        history = config_service.get_history(sample_config, today)
        assert history == 90

    def test_get_history_with_date(self, config_service):
        config = {"general": {"history": "2023-11-01"}}
        today = datetime.strptime("2023-12-01", "%Y-%m-%d")
        history = config_service.get_history(config, today)
        assert history == 30

    def test_get_data_source(self, config_service, sample_config):
        data_source = config_service.get_data_source(sample_config)
        assert data_source == "azuredevops"

    def test_get_data_sources(self, config_service, sample_config):
        sources = config_service.get_data_sources(sample_config)
        assert len(sources) == 2
        assert sources[0]["name"] == "source1"

    def test_read_config(self, config_service, temp_config_file, sample_config):
        config_data = config_service.read_config(temp_config_file)
        assert config_data == sample_config

    def test_check_if_file_exists_with_missing_file(self, config_service):
        with pytest.raises(FileNotFoundError):
            config_service.check_if_file_exists("nonexistent.json", raise_if_not_found=True)

    def test_get_target_date_with_days(self, config_service):
        today = datetime.strptime("2023-12-01", "%Y-%m-%d")
        forecast_config = {"targetDate": 30}
        target_date = config_service.get_target_date(forecast_config, today)
        assert target_date == (today + timedelta(30)).date()

    def test_get_target_date_with_date_string(self, config_service):
        today = datetime.strptime("2023-12-01", "%Y-%m-%d")
        forecast_config = {"targetDate": "2024-01-01"}
        target_date = config_service.get_target_date(forecast_config, today)
        assert target_date == datetime.strptime("2024-01-01", "%Y-%m-%d").date()

    def test_get_charts(self, config_service, sample_config):
        charts = config_service.get_charts(sample_config)
        assert len(charts) == 1
        assert charts[0]["type"] == "burndown"
        assert charts[0]["trendSettings"]["window"] == 14
