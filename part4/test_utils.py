from utils import transform_backends_from_config
from models import Server

import pytest
import yaml

def test_transform_backends_from_config():
    input = yaml.safe_load('''
        hosts:
          - host: www.mango.com
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.apple.com
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    output = transform_backends_from_config(input)
    assert list(output.keys()) == ["www.mango.com", "www.apple.com"]
    print(output)
    #assert isinstance(list(output.values())[0][0], Server) == isinstance(output["www.mango.com"][0], Server)
    #assert list(output.values())[1] == isinstance(output["www.mango.com"][1], Server)
    #assert list(output.values())[0] == isinstance(output["www.apple.com"][0], Server)
    #assert list(output.values())[1] == isinstance(output["www.mango.com"][1], Server)

