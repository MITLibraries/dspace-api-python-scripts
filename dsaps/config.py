import logging
import os
import yaml

import smart_open


class Config:
    REQUIRED_ENV_VARS = ["SOURCE_CONFIG", "DSPACE_URL", "DSPACE_EMAIL", "DSPACE_PASSWORD"]

    OPTIONAL_ENV_VARS = []

    def __init__(self, config_file: str) -> None:
        self.config_file = config_file

    def __getattr__(self, name: str):
        """Provide dot notation access to configurations and env vars on this class."""
        if name in self.REQUIRED_ENV_VARS or name in self.OPTIONAL_ENV_VARS:
            return os.getenv(name)
        message = f"'{name}' not a valid configuration variable"
        raise AttributeError(message)

    def check_required_env_vars(self) -> None:
        """Method to raise exception if required env vars not set."""
        missing_vars = [var for var in self.REQUIRED_ENV_VARS if not os.getenv(var)]
        if missing_vars:
            message = f"Missing required environment variables: {', '.join(missing_vars)}"
            raise OSError(message)

    @classmethod
    def load_source_config(cls, config_file: str) -> dict:
        with smart_open.open(config_file, "r") as file:
            return yaml.safe_load(file)

    @property
    def source_settings(self) -> dict:
        return self.load_source_config(self.config_file)["settings"]

    @property
    def source_field_mapping(self) -> dict:
        return self.load_source_config(self.config_file)["mapping"]


def configure_logger(logger: logging.Logger, verbose: bool, output_file: str):
    if os.path.exists("logs") is False:
        os.mkdir("logs")

    if verbose:
        logging.basicConfig(
            filename=f"logs/{output_file}.log",
            format="%(asctime)s %(levelname)s %(name)s.%(funcName)s() line %(lineno)d: "
            "%(message)s",
            force=True,
        )
        logger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(
            filename=f"logs/{output_file}.log",
            format="%(asctime)s %(levelname)s %(name)s.%(funcName)s(): %(message)s",
            force=True,
        )
        logger.setLevel(logging.INFO)
    return (
        f"Logger '{logger.name}' configured with level="
        f"{logging.getLevelName(logger.getEffectiveLevel())}"
    )
