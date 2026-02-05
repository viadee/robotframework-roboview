import builtins

from roboview.core.config import CONFIG, Settings, get_settings, print_warning


def test_config_ansi_constants():
    assert isinstance(CONFIG.YELLOW, str) and CONFIG.YELLOW.startswith("\033[")
    assert isinstance(CONFIG.RED, str) and CONFIG.RED.startswith("\033[")
    assert isinstance(CONFIG.RESET, str) and CONFIG.RESET.startswith("\033[")
    assert isinstance(CONFIG.BOLD, str) and CONFIG.BOLD.startswith("\033[")


def test_print_warning_writes_colored_message(monkeypatch):
    printed = {}

    def fake_print(*args, **kwargs):
        printed["value"] = args[0]

    monkeypatch.setattr(builtins, "print", fake_print)

    message = "Something might be wrong"
    print_warning(message)

    out = printed["value"]
    assert "WARNING:" in out
    assert message in out
    assert CONFIG.YELLOW in out
    assert CONFIG.BOLD in out
    assert out.endswith(CONFIG.RESET)


def test_settings_defaults_without_env(monkeypatch):
    for key in [
        "PROJECT_NAME",
        "API_VERSION_STR",
        "APP_VERSION",
        "ENVIRONMENT",
        "LOG_LEVEL",
    ]:
        monkeypatch.delenv(key, raising=False)

    settings = Settings()

    assert settings.PROJECT_NAME == "RoboView"
    assert settings.API_VERSION_STR == "/api/v1"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.ENVIRONMENT == "production"
    assert settings.LOG_LEVEL == "INFO"
    assert settings.BACKEND_CORS_ORIGINS == ["http://localhost:8000"]
    assert settings.HTTP_METHODS == ["GET", "POST", "PUT", "DELETE"]


def test_settings_can_be_overridden_by_env(monkeypatch):
    monkeypatch.setenv("PROJECT_NAME", "CustomProject")
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.PROJECT_NAME == "CustomProject"
    assert settings.ENVIRONMENT == "development"
    assert settings.LOG_LEVEL == "DEBUG"


def test_get_settings_is_cached(monkeypatch):
    get_settings.cache_clear()

    monkeypatch.setenv("PROJECT_NAME", "CachedProject")

    s1 = get_settings()
    s2 = get_settings()

    assert isinstance(s1, Settings)
    assert s1 is s2
    assert s1.PROJECT_NAME == "CachedProject"

    monkeypatch.setenv("PROJECT_NAME", "ChangedAfterCache")
    s3 = get_settings()
    assert s3 is s1
    assert s3.PROJECT_NAME == "CachedProject"