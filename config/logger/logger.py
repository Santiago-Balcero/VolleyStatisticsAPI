import logging
from logging.config import dictConfig
from config.logger.logger_config import LogConfig


dictConfig(LogConfig().dict())
LOG = logging.getLogger("volleystats")
