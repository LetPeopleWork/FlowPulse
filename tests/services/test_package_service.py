import pytest
from unittest.mock import patch, MagicMock
from flowpulse.services.PackageService import PackageService


@pytest.fixture
@pytest.mark.integration
def package_service():
    return PackageService()


@pytest.mark.integration
def test_init(package_service):
    assert package_service.package_name == "flowpulse"
    assert hasattr(package_service, "current_version")


@patch("flowpulse.services.PackageService.version")
@pytest.mark.integration
def test_print_current_version(mock_version, capsys):
    mock_version.return_value = "1.0.0"
    service = PackageService()
    service.print_current_version()

    captured = capsys.readouterr()
    assert "flowpulse@1.0.0" in captured.out
    assert "=" * 64 in captured.out


@patch("requests.get")
@patch("flowpulse.services.PackageService.version")
@pytest.mark.integration
def test_check_for_updates_new_version_available(mock_version, mock_requests, capsys):
    mock_version.return_value = "1.0.0"
    mock_response = MagicMock()
    mock_response.json.return_value = {"info": {"version": "1.1.0"}}
    mock_requests.return_value = mock_response

    service = PackageService()
    service.check_for_updates()

    captured = capsys.readouterr()
    assert "Update available: 1.1.0" in captured.out
    assert "python -m pip install --upgrade flowpulse" in captured.out


@patch("requests.get")
@patch("flowpulse.services.PackageService.version")
@pytest.mark.integration
def test_check_for_updates_same_version(mock_version, mock_requests, capsys):
    mock_version.return_value = "1.0.0"
    mock_response = MagicMock()
    mock_response.json.return_value = {"info": {"version": "1.0.0"}}
    mock_requests.return_value = mock_response

    service = PackageService()
    service.check_for_updates()

    captured = capsys.readouterr()
    assert "Update available" not in captured.out


@patch("requests.get")
@pytest.mark.integration
def test_check_for_updates_error_handling(mock_requests, capsys):
    mock_requests.side_effect = Exception("Connection error")

    service = PackageService()
    service.check_for_updates()

    captured = capsys.readouterr()
    assert "Error checking for updates" in captured.out


@pytest.mark.integration
def test_print_logo(capsys):
    service = PackageService()
    service.print_logo()

    captured = capsys.readouterr()
    assert "FlowPulse" in captured.out or "/$$" in captured.out
