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

def process_rules(config, host, rules, modify):
    modify_options = {"header": "header_rules", 
                      "param": "param_rules"}
    for entry in config.get('hosts', []):
        if host == entry['host']: 
            header_rules = entry.get(modify_options[modify], {})
            for instruction, modify_headers in header_rules.items():
                if instruction == "add":
                    rules.update(modify_headers)
                if instruction == "remove":
                    for key in modify_headers.keys():
                        if key in rules:
                            rules.pop(key) 
    return rules

def process_rewrite_rules(config, host, path):
    for entry in config.get('hosts', []):
        if host == entry['host']:
            rewrite_rules = entry.get('rewrite_rules', {})
            for current_path, new_path in rewrite_rules["replace"].items():
                return path.replace(current_path, new_path)
