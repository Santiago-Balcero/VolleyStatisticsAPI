import logging
from logging.config import dictConfig
from config.logger.loggerConfig import LogConfig

dictConfig(LogConfig().dict())
LOG = logging.getLogger("volleystats")