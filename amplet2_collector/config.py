import logging
import configparser

# XXX if this is all of it, move into main module?
def parse_config(filename):
    logger = logging.getLogger(__name__)
    logger.debug("Loading configuration from '%s'", filename)

    config = configparser.SafeConfigParser()

    try:
        config.read_file(open(filename))
    except IOError as err:
        logger.error("Failed to load configuration: %s", err)
        return None

    return config
