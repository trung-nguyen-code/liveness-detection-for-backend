import logging
import os
from logging import config

from app.infrastructure.elasticsearch.database import Elastic
from app.infrastructure.elasticsearch.user.user_builder import Builder
from app.infrastructure.mongo.database import Mongo

from app.constants.settings import settings

absolute_path = os.path.dirname(__file__)


def get_elastic():
    elastic = Elastic()
    return elastic


def get_builder():
    query_builder = Builder()
    return query_builder


def get_mongo():
    mongo = Mongo()
    return mongo


config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

score_settings_path = os.path.join(absolute_path, settings.SETTING_PATH)
# score_settings_path_v2 = os.path.join(absolute_path, settings.SETTING_PATH_2)
