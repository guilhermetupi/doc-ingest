import pytest

from doc_ingest.config.env import Settings


class TestSettings:
    """Tests for the Settings configuration."""

    def test_settings_database_url(self, monkeypatch):
        """Settings should expose a database_url attribute."""
        monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
        settings = Settings()
        assert settings.database_url == "sqlite:///test.db"

    def test_settings_defaults(self):
        """Settings class should have env_file config pointing to '.env'."""
        assert Settings.model_config.get("env_file") == ".env"
