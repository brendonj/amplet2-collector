import logging
import configparser

def parse_config(filename):
    logger = logging.getLogger(__name__)
    logger.debug("Loading configuration from '%s'", filename)

    config = configparser.ConfigParser()

    try:
        config.read_file(open(filename))
    except IOError as err:
        logger.error("Failed to load configuration: %s", err)
        return None

    return config
