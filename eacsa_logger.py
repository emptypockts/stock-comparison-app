import logging.config
import os
import sys
import threading
from pathlib import Path
from typing import Optional
from app_constants import LOG_LEVEL
_CONFIGURED = False

def setup_logging(
  app_name: str = "STOCK-COMPARISON-APP",
  log_dir: str | Path = "logs",
  level : Optional[str] = None,
  console: bool = True
)->None:
    """
    Configure repo logging
    Features:
    - Console logging,
    - Rotating app file.
    - Separate rotating error log file.
    - No duplicate handlers.
    - Captures warnings.
    - Global exception logging.
    """
    global _CONFIGURED

    if _CONFIGURED:
        return
    
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True,exist_ok=True)

    handlers : dict = {
        "file":{
            "class": "logging.handlers.RotatingFileHandler",
            "level": LOG_LEVEL,
            "formatter": "detailed",
            "filename": str(log_dir / f"{app_name}.log"),
            "maxBytes": 10 * 1024 * 1024 ,
            "backupCount": 10,
            "encoding": "utf-8"
        },
        "error_file":{
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": str(log_dir / f"{app_name}.log"),
            "maxBytes": 10 * 1024 * 1024,
            "backupCount": 10,
            "encoding": "utf-8"
        }
    }

    root_handlers = ["file", "error_file"]

    if console:
        handlers['console'] = {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "console",
            "stream": "ext://sys.stdout" 
        }
        root_handlers.insert(0,"console")

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format" : "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "detailed":{
                "format": (
                    "%(asctime)s | %(levelname)-8s | %(name)s |"
                    "%(filename)s:%(lineno)d | %(funcName)s() | %(message)s"
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": handlers,
        "root": {
            "level": LOG_LEVEL,
            "handlers": root_handlers,
        },
        "loggers": {
            "urllib3": {
                "level": "WARNING",
                "propagate": True,
            },
            "asyncio": {
                "level": "WARNING",
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(config)
    logging.captureWarnings(True)

    install_exception_hooks(app_name)
    _CONFIGURED = True

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger.
    Usage: 
        logger = get_logger(__name__)
    """
    return logging.getLogger(name if name else __name__ )
    
def install_exception_hooks(app_name: str = "app") -> None:
    """
    Log uncaught exceptions globally.
    """
    logger = logging.getLogger(app_name)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical(
            "Uncaught exception",
            exc_info = (exc_type, exc_value, exc_traceback)
        )
    sys.excepthook = handle_exception

    def handle_thread_exception(args: threading.ExceptHookArgs):
        logger.critical(
            "Uncaught thread exception",
            exc_info = (args.exc_type, args.exc_value, args.exc_traceback)
        )
    
    threading.excepthook = handle_thread_exception



if __name__ == "__main__":
    setup_logging(app_name = __name__)
    eacsa_logger= get_logger(__name__)
    
    eacsa_logger.info("testing start")

    try:
        1/1
    except ZeroDivisionError:
        eacsa_logger.exception("error dividing")

    eacsa_logger.info("testing finished")
