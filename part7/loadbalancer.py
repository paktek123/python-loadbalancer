from flask import Flask, request
import requests, random
from utils import load_configuration, transform_backends_from_config, get_healthy_server, process_rules, process_rewrite_rules, process_firewall_rules_flag
from tasks import healthcheck
import sys

loadbalancer = Flask(__name__)
config = load_configuration('loadbalancer.yaml')
register = transform_backends_from_config(config)

@loadbalancer.route("/")
@loadbalancer.route("/<path>")
def router(path="/"):
    updated_register = healthcheck(register)
    host_header = request.headers["Host"]
    if not process_firewall_rules_flag(config, host_header, request.environ["REMOTE_ADDR"], "/"+path):
        return "Forbidden", 403
    for entry in config["hosts"]:
        if host_header == entry["host"]:
            healthy_server = get_healthy_server(entry["host"], updated_register)
            if not healthy_server:
                return "No Backends servers available", 503
            headers = process_rules(config, host_header, {k:v for k,v in request.headers.items()}, "header" )
            params = process_rules(config, host_header, {k:v for k,v in request.args.items()}, "param")
            rewrite_path = ""
            if path == "v1":
                rewrite_path = process_rewrite_rules(config, host_header, path)
            healthy_server.open_connections += 1
            response = requests.get("http://{}{}".format(healthy_server.endpoint, "/" + rewrite_path), headers=headers, params=params)
            healthy_server.open_connections -= 1
            return response.content, response.status_code
    
    for entry in config["paths"]:
        if ("/" + path) == entry["path"]:
            healthy_server = get_healthy_server(entry["path"], register)
            if not healthy_server:
                return "No Backends servers available", 503
            response = requests.get("http://{}".format(healthy_server.endpoint))
            return response.content, response.status_code

    return "Not Found", 404
