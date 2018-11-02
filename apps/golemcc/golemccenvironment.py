from os import path

from golem.core.common import get_golem_path
from golem.docker.environment import DockerEnvironment

class GolemccTaskEnvironment(DockerEnvironment):
    DOCKER_IMAGE = "golemfactory/golemcc"
    DOCKER_TAG = "1.0"
    ENV_ID = "golemcc"
    APP_DIR = path.join(get_golem_path(), 'apps', 'golemcc')
    SCRIPT_NAME = "docker_golemcctask.py"
    SHORT_DESCRIPTION = "Golemcc PoC"
