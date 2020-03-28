from flask import Flask, request
import requests, random
import yaml

loadbalancer = Flask(__name__)

def load_configuration(path):
    with open(path) as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
    return config

config = load_configuration('loadbalancer.yaml')

@loadbalancer.route('/')
def router():
    host_header = request.headers["Host"]
    for entry in config["hosts"]:
        if host_header == entry["host"]:
            response = requests.get("http://{}".format(random.choice(entry["servers"])))
            return response.content, response.status_code
    
    return "Not Found", 404

@loadbalancer.route("/<path>")
def path_router(path):
    for entry in config["paths"]:
        if ("/" + path) == entry["path"]:
            response = requests.get("http://{}".format(random.choice(entry["servers"])))
            return response.content, response.status_code

    return "Not Found", 404
