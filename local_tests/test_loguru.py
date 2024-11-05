from loguru import logger

# Caution, "diagnose=True" is the default and may leak sensitive data in prod
# logger.add("default_{time}.log", backtrace=True, diagnose=True)
logger.add("default_{time}.log", diagnose=True)


def some_function():
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    logger.exception("This is an ERROR level message with exc_info.")

    try:
        print("OMG Exception")
        raise Exception("Random exception!")
    except Exception:
        logger.exception("This is an ERROR level message with a stack trace!")


if __name__ == "__main__":
    some_function()
