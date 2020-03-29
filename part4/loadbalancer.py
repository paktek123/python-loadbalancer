from flask import Flask, request
import requests, random
from threading import Thread
from utils import load_configuration, transform_backends_from_config, get_healthy_server
from tasks import background_healthcheck

loadbalancer = Flask(__name__)

config = load_configuration('loadbalancer.yaml')
register = transform_backends_from_config(config)
thread = Thread(target=background_healthcheck, args=(register, 3))
thread.daemon = True
thread.start()

@loadbalancer.route('/')
def router():
    host_header = request.headers["Host"]
    for entry in config["hosts"]:
        if host_header == entry["host"]:
            healthy_server = get_healthy_server(entry["host"], register)
            response = requests.get("http://{}".format(healthy_server))
            return response.content, response.status_code
    
    return "Not Found", 404

@loadbalancer.route("/<path>")
def path_router(path):
    for entry in config["paths"]:
        if ("/" + path) == entry["path"]:
            response = requests.get("http://{}".format(random.choice(entry["servers"])))
            return response.content, response.status_code

    return "Not Found", 404

if __name__ == '__main__':
    loadbalancer.run(host="0.0.0.0", port=7081, debug=True)
