""" Runing tests of common module"""

import logging
import logging.config

import yaml


def main():
    """Entry point to run"""
    # Parsing YAML file
    config_path = "config/common.yaml"
    config = yaml.safe_load(open(config_path))
    log_config = config["logging"]
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(__name__)
    logger.info("nothing")


if __name__ == "__main__":
    main()
