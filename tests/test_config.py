from dsaps.config import Config

CONFIG = Config(config_file="tests/fixtures/config/source_simple.json")


def test_load_source_config():
    source_config = Config.load_source_config("tests/fixtures/config/source_simple.json")
    assert "settings" in source_config
    assert "mapping" in source_config
