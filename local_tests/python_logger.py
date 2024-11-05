import logging
import sys


def setup_logger(log_file="default.log"):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if log_file.endswith(".log"):
        filename = log_file
    else:
        filename = log_file + ".log"

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Create file handler
    file_handler = logging.FileHandler(filename)
    file_handler.setLevel(logging.INFO)

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Create and configure the logger
log = setup_logger()

if __name__ == "__main__":
    log.debug("This is a debug message")
    log.info("This is an info message")
    log.warning("This is a warning message")
    log.error("This is an error message")
    log.critical("This is a critical message")
    log.fatal("This is a simple FATAL level message")
    log.exception("This is an ERROR level message with exc_info.")

    try:
        print("OMG Exception")
        raise Exception("Random exception!")
    except Exception:
        log.exception("This is an ERROR level message with a stack trace!")
