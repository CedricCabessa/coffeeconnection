import logging
import sys

LOGGER = logging.getLogger()


def setup_logger():
    logger = LOGGER
    logger.setLevel(logging.DEBUG)

    # File logger
    file_handler = logging.FileHandler("coffeeconnection.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    )
    # Console logger
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
