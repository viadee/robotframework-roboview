import logging

from roboview.core.logging import setup_logging


def test_setup_logging_uses_basic_config_in_production(monkeypatch):
    calls = {}

    def fake_basicConfig(**kwargs):
        calls["kwargs"] = kwargs

    class FakeSettings:
        ENVIRONMENT = "production"
        LOG_LEVEL = "INFO"

    def fake_get_settings():
        return FakeSettings()

    monkeypatch.setattr("roboview.core.logging.logging.basicConfig", fake_basicConfig)
    monkeypatch.setattr("roboview.core.logging.get_settings", fake_get_settings)

    setup_logging()

    assert calls["kwargs"]["level"] == logging.INFO
    assert "%(asctime)s" in calls["kwargs"]["format"]


def test_setup_logging_uses_coloredlogs_outside_production(monkeypatch):
    calls = {}

    def fake_install(**kwargs):
        calls["kwargs"] = kwargs

    class FakeSettings:
        ENVIRONMENT = "development"
        LOG_LEVEL = "DEBUG"

    def fake_get_settings():
        return FakeSettings()

    monkeypatch.setattr("roboview.core.logging.coloredlogs.install", fake_install)
    monkeypatch.setattr("roboview.core.logging.get_settings", fake_get_settings)

    setup_logging()

    assert calls["kwargs"]["level"] == logging.DEBUG
    assert "%(asctime)s" in calls["kwargs"]["fmt"]
    assert calls["kwargs"]["reconfigure"] is True


def test_setup_logging_falls_back_to_info_for_invalid_level(monkeypatch):
    calls = {}

    def fake_basicConfig(**kwargs):
        calls["kwargs"] = kwargs

    class FakeSettings:
        ENVIRONMENT = "production"
        LOG_LEVEL = "NOT_A_LEVEL"

    def fake_get_settings():
        return FakeSettings()

    monkeypatch.setattr("roboview.core.logging.logging.basicConfig", fake_basicConfig)
    monkeypatch.setattr("roboview.core.logging.get_settings", fake_get_settings)

    setup_logging()

    assert calls["kwargs"]["level"] == logging.INFO