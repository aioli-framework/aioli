import sys

import logging
import logging.config

from copy import copy


LOGGING_CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=True,
    loggers={
        "root": {
            "level": "WARN",
            "handlers": ["unit_console"],
            "propagate": False
        },
        "aioli": {
            "level": "WARN",
            "handlers": ["unit_console"],
            "propagate": False
        },
        "uvicorn": {
            "level": "WARN",
            "handlers": ["unit_console"],
            "propagate": False
        },
    },
    handlers={
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": sys.stdout,
        },
        "request_console": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": sys.stdout,
        },
        "access_console": {
            "class": "logging.StreamHandler",
            "formatter": "access",
            "stream": sys.stdout,
        },
        "unit_console": {
            "class": "logging.StreamHandler",
            "formatter": "unit",
            "stream": sys.stdout,
        },
    },
    formatters={
        "unit": {
            "format": "[%(levelname)1.1s %(asctime)s.%(msecs)03d %(name)s] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "class": "logging.Formatter",
        },
        "access": {
            "format": "[%(levelname)1.1s %(asctime)s.%(msecs)03d %(process)d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "class": "logging.Formatter",
        },
        "generic": {
            "format": "[%(levelname)1.1s %(asctime)s.%(msecs)03d] %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "class": "logging.Formatter",
        },
    },
)


def setup_logging(level):
    config = copy(LOGGING_CONFIG_DEFAULTS)

    for name, logger in config['loggers'].items():
        logger['level'] = level.upper() if level else logging.WARN

    logging.config.dictConfig(config)
