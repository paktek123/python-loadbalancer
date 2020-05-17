from utils import get_healthy_server, transform_backends_from_config, process_rules, process_rewrite_rules, least_connections, process_firewall_rules_flag
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
        paths:
          - path: /mango
            servers:
              - localhost:8081
              - localhost:8082
          - path: /apple
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    output = transform_backends_from_config(input)
    assert list(output.keys()) == ["www.mango.com", "www.apple.com", "/mango", "/apple"]
    assert output["www.mango.com"][0] == Server("localhost:8081")
    assert output["www.mango.com"][1] == Server("localhost:8082")
    assert output["www.apple.com"][0] == Server("localhost:9081")
    assert output["www.apple.com"][1] == Server("localhost:9082")
    assert output["/mango"][0] == Server("localhost:8081")
    assert output["/mango"][1] == Server("localhost:8082")
    assert output["/apple"][0] == Server("localhost:9081")
    assert output["/apple"][1] == Server("localhost:9082")

def test_get_healthy_server():
    host = "www.apple.com"
    healthy_server = Server("localhost:8081")
    unhealthy_server = Server("localhost:8082")
    unhealthy_server.healthy = False
    register = {"www.mango.com": [healthy_server, unhealthy_server], 
                "www.apple.com": [healthy_server, healthy_server],
                "www.orange.com": [unhealthy_server, unhealthy_server],
                "/mango": [healthy_server, unhealthy_server],
                "/apple": [unhealthy_server, unhealthy_server]}
    assert get_healthy_server("www.mango.com", register) == healthy_server
    assert get_healthy_server("www.apple.com", register) == healthy_server
    assert get_healthy_server("www.orange.com", register) == None
    assert get_healthy_server("/mango", register) == healthy_server
    assert get_healthy_server("/apple", register) == None
    
def test_process_header_rules():
    input = yaml.safe_load('''
        hosts:
          - host: www.mango.com
            header_rules:
              add: 
                MyCustomHeader: Test
              remove: 
                Host: www.mango.com
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.apple.com
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /mango
            servers:
              - localhost:8081
              - localhost:8082
          - path: /apple
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    headers = {"Host": "www.mango.com"}
    results = process_rules(input, "www.mango.com", headers, "header")
    assert results == {"MyCustomHeader": "Test"}
    

def test_process_param_rules():
    input = yaml.safe_load('''
        hosts:
          - host: www.mango.com
            param_rules:
              add:
                MyCustomParam: Test
              remove:
                RemoveMe: Remove
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.apple.com
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /mango
            servers:
              - localhost:8081
              - localhost:8082
          - path: /apple
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    params = {"RemoveMe": "Remove"}
    results = process_rules(input, "www.mango.com", params, "param")
    assert results == {"MyCustomParam": "Test"}

def test_process_rewrite_rules():
    input = yaml.safe_load('''
        hosts:
          - host: www.mango.com
            rewrite_rules:
              replace:
                v1: v2
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.apple.com
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /mango
            servers:
              - localhost:8081
              - localhost:8082
          - path: /apple
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    path = "localhost:8081/v1"
    results = process_rewrite_rules(input, "www.mango.com", path)
    assert results == "localhost:8081/v2"

def test_least_connections():
    backend1 = Server("localhost:8081")
    backend1.open_connections = 10
    backend2 = Server("localhost:8082")
    backend2.open_connections = 5
    backend3 = Server("localhost:8083")
    backend3.open_connections = 2
    servers = [backend1, backend2, backend3]
    result = least_connections(servers)
    assert result == backend3

def test_least_connections_empty_list():
    result = least_connections([])
    assert result == None

def test_process_firewall_rules_reject():
    input = yaml.safe_load('''
        hosts:
          - host: www.mango.com
            firewall_rules:
              ip_reject:
                - 10.192.0.1
                - 10.192.0.2
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.apple.com
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /mango
            servers:
              - localhost:8081
              - localhost:8082
          - path: /apple
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    results = process_firewall_rules_flag(input, "www.mango.com", "10.192.0.1")
    assert results == False

def test_process_firewall_rules_accept():
    input = yaml.safe_load('''
        hosts:
          - host: www.mango.com
            firewall_rules:
              ip_reject:
                - 10.192.0.1
                - 10.192.0.2
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.apple.com
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /mango
            servers:
              - localhost:8081
              - localhost:8082
          - path: /apple
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    results = process_firewall_rules_flag(input, "www.mango.com", "55.55.55.55")
    assert results == True

def test_process_firewall_rules_path_reject():
    input = yaml.safe_load('''
        hosts:
          - host: www.mango.com
            firewall_rules:
              path_reject:
                - /messages
                - /apps
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.apple.com
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /mango
            servers:
              - localhost:8081
              - localhost:8082
          - path: /apple
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    results = process_firewall_rules_flag(input, "www.mango.com", path="/apps")
    assert results == False

def test_process_firewall_rules_path_accept():
    input = yaml.safe_load('''
        hosts:
          - host: www.mango.com
            firewall_rules:
              path_reject:
                - /messages
                - /apps
            servers:
              - localhost:8081
              - localhost:8082
          - host: www.apple.com
            servers:
              - localhost:9081
              - localhost:9082
        paths:
          - path: /mango
            servers:
              - localhost:8081
              - localhost:8082
          - path: /apple
            servers:
              - localhost:9081
              - localhost:9082
    ''')
    results = process_firewall_rules_flag(input, "www.mango.com", path="/pictures")
    assert results == True
