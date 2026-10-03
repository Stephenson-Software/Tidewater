import io
import os

import pytest

from tidewater import config as configModule
from tidewater import usageReporting
from tidewater.config import Config


class FakeClient:
    """Stands in for TraceClient wherever a test needs an *enabled* client:
    the real one starts a thread that posts to the trace service."""

    def __init__(self, endpoint, program, key=None, enabled=True):
        self.args = (endpoint, program, key, enabled)
        self.enabled = enabled
        self.reports = []

    def report(self, name, value=None, tags=None):
        self.reports.append((name, tags))


@pytest.fixture
def fakeClient(monkeypatch):
    built = []

    def build(*args, **kwargs):
        client = FakeClient(*args, **kwargs)
        built.append(client)
        return client

    monkeypatch.setattr(usageReporting, "TraceClient", build)
    return built


@pytest.fixture
def reportingOn(monkeypatch):
    monkeypatch.setenv("TIDEWATER_USAGE_REPORTING_ENABLED", "true")


def versionOnDisk():
    with open("version.txt", encoding="utf-8") as versionFile:
        return versionFile.read().strip()


# --- config ---------------------------------------------------------------


def test_config_defaults_when_nothing_is_set(monkeypatch):
    for name in (
        "TIDEWATER_SAVE_DIR",
        "TIDEWATER_USAGE_REPORTING_ENABLED",
        "TIDEWATER_USAGE_REPORTING_ENDPOINT",
        "TIDEWATER_USAGE_REPORTING_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    config = Config()
    assert config.dataDirectory == "data"
    assert config.usageReportingEnabled is True
    assert (
        config.usageReportingEndpoint == configModule.USAGE_REPORTING_ENDPOINT_DEFAULT
    )
    assert config.usageReportingKey == configModule.USAGE_REPORTING_KEY_DEFAULT


@pytest.mark.parametrize("value", ["0", "false", "no", "off", "  OFF ", "False"])
def test_each_false_value_turns_reporting_off(monkeypatch, value):
    monkeypatch.setenv("TIDEWATER_USAGE_REPORTING_ENABLED", value)
    assert Config().usageReportingEnabled is False


@pytest.mark.parametrize("value", ["", "   ", "true", "1", "maybe"])
def test_anything_else_leaves_reporting_on(monkeypatch, value):
    monkeypatch.setenv("TIDEWATER_USAGE_REPORTING_ENABLED", value)
    assert Config().usageReportingEnabled is True


def test_endpoint_and_key_overrides_are_stripped_and_blank_ones_ignored(monkeypatch):
    monkeypatch.setenv("TIDEWATER_USAGE_REPORTING_ENDPOINT", " http://localhost:9 ")
    monkeypatch.setenv("TIDEWATER_USAGE_REPORTING_KEY", "  ")
    config = Config()
    assert config.usageReportingEndpoint == "http://localhost:9"
    assert config.usageReportingKey == configModule.USAGE_REPORTING_KEY_DEFAULT


def test_the_save_dir_variable_moves_the_data_directory(monkeypatch, tmp_path):
    monkeypatch.setenv("TIDEWATER_SAVE_DIR", str(tmp_path / "elsewhere"))
    assert Config().dataDirectory == str(tmp_path / "elsewhere")


# --- the version ------------------------------------------------------------


def test_read_version_reads_version_txt():
    assert usageReporting.readVersion() == versionOnDisk()
    assert usageReporting.versionTags() == {"version": versionOnDisk()}


def test_a_missing_or_empty_version_file_gives_no_version(tmp_path, monkeypatch):
    assert usageReporting.readVersion(str(tmp_path / "absent.txt")) is None
    empty = tmp_path / "empty.txt"
    empty.write_text("  \n", encoding="utf-8")
    assert usageReporting.readVersion(str(empty)) is None

    monkeypatch.setattr(usageReporting, "readVersion", lambda path=None: None)
    assert usageReporting.versionTags() is None


# --- the client ---------------------------------------------------------------


def test_the_browser_build_never_builds_an_enabled_client(monkeypatch, reportingOn):
    monkeypatch.setattr(usageReporting, "isBrowserBuild", lambda: True)
    client = usageReporting.createClient(Config())
    assert client.enabled is False


def test_tidewaters_own_setting_switches_the_client_off():
    # The autouse fixture sets TIDEWATER_USAGE_REPORTING_ENABLED=false.
    client = usageReporting.createClient(Config())
    assert client.enabled is False
    assert client.disabled_reason == "config"


@pytest.mark.parametrize(
    "name,value", [("TRACE_USAGE_REPORTING", "off"), ("DO_NOT_TRACK", "1")]
)
def test_the_shared_opt_outs_win_over_tidewaters_setting(
    monkeypatch, reportingOn, name, value
):
    monkeypatch.setenv(name, value)
    client = usageReporting.createClient(Config())
    assert client.enabled is False
    assert client.disabled_reason == "environment"


def test_an_enabled_client_is_built_from_the_config(fakeClient, reportingOn):
    config = Config()
    usageReporting.createClient(config)
    assert fakeClient[0].args == (
        config.usageReportingEndpoint,
        usageReporting.PROGRAM_NAME,
        config.usageReportingKey,
        True,
    )


# --- the first-run notice -----------------------------------------------------


def test_the_notice_is_shown_once_and_left_as_a_marker():
    config = Config()
    first, second = io.StringIO(), io.StringIO()
    assert usageReporting.showNoticeOnce(config, first) is True
    assert usageReporting.showNoticeOnce(config, second) is False
    assert first.getvalue() == usageReporting.NOTICE + "\n"
    assert second.getvalue() == ""
    with open(usageReporting.noticeMarkerPath(config), encoding="utf-8") as marker:
        assert marker.read() == usageReporting.NOTICE + "\n"


def test_an_unwritable_marker_still_prints_the_notice_every_time(monkeypatch, tmp_path):
    blocker = tmp_path / "a-file"
    blocker.write_text("", encoding="utf-8")
    monkeypatch.setenv("TIDEWATER_SAVE_DIR", str(blocker / "saves"))
    config = Config()
    for _ in range(2):
        output = io.StringIO()
        assert usageReporting.showNoticeOnce(config, output) is True
        assert usageReporting.NOTICE in output.getvalue()


def test_the_notice_says_how_to_turn_it_off():
    assert "TIDEWATER_USAGE_REPORTING_ENABLED=false" in usageReporting.NOTICE
    assert "TRACE_USAGE_REPORTING=off" in usageReporting.NOTICE
    assert usageReporting.DETAILS_URL in usageReporting.NOTICE


# --- start ----------------------------------------------------------------------


def test_a_disabled_start_says_nothing_and_leaves_no_marker():
    config = Config()
    output = io.StringIO()
    client = usageReporting.start(config, output)
    assert client.enabled is False
    assert output.getvalue() == ""
    assert not os.path.exists(usageReporting.noticeMarkerPath(config))


def test_an_enabled_start_reports_startup_and_notices_only_the_first_time(
    fakeClient, reportingOn
):
    config = Config()
    first, second = io.StringIO(), io.StringIO()
    usageReporting.start(config, first)
    usageReporting.start(config, second)
    assert usageReporting.NOTICE in first.getvalue()
    assert second.getvalue() == ""
    assert [client.reports for client in fakeClient] == [
        [("startup", {"version": versionOnDisk()})]
    ] * 2
