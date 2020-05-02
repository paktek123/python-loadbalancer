from tasks import healthcheck
from utils import transform_backends_from_config

import pytest
import yaml

def test_healthcheck():
    config = yaml.safe_load('''
        hosts:
          - host: www.mango.com
            servers:
              - localhost:8081
              - localhost:8888
          - host: www.apple.com
            servers:
              - localhost:9081
              - localhost:4444
    ''')
    register = healthcheck(transform_backends_from_config(config))

    assert register["www.apple.com"][0].healthy == True
    assert register["www.apple.com"][1].healthy == False
    assert register["www.mango.com"][0].healthy == True
    assert register["www.mango.com"][1].healthy == False
