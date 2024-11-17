from python_logger import log


def some_function():
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


if __name__ == "__main__":
    some_function()
