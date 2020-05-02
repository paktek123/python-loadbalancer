from models import Server
import yaml
import random

def load_configuration(path):
    with open(path) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config

def transform_backends_from_config(config):
    register = {}
    for entry in config.get('hosts', []):
        register.update({entry["host"]: [Server(endpoint) for endpoint in entry["servers"]]})
    for entry in config.get('paths', []):
        register.update({entry["path"]: [Server(endpoint) for endpoint in entry["servers"]]})
    return register

def get_healthy_server(host, register):
    try:
        return random.choice([server for server in register[host] if server.healthy])
    except IndexError:
        return None
