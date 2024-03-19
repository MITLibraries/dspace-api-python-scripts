from dsaps.config import Config

CONFIG = Config(config_file="tests/fixtures/config/source.json")


def test_load_source_config():
    source_config = Config.load_source_config("tests/fixtures/config/source.json")
    assert "settings" in source_config
    assert "mapping" in source_config


def test_source_settings_with_id_configs():
    source_settings = CONFIG.source_settings
    assert "id" in source_settings
