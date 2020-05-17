from loadbalancer import loadbalancer

import pytest
import re

@pytest.fixture
def client():
    with loadbalancer.test_client() as client:
        yield client

def test_host_routing_mango(client):
    result = client.get('/', headers={"Host":"www.mango.com"}, query_string={"RemoveMe": "Remove"})
    assert re.match("This is the mango application. Serving on localhost:\d+. Custom Header: Test, Host Header: localhost:\d+, Custom Param: Test", result.data.decode('utf-8')) != None

def test_host_routing_apple(client):
    result = client.get('/', headers={"Host":"www.apple.com"})
    assert b'This is the apple application. Serving on localhost:9082. Custom Header: None, Host Header: www.apple.com, Custom Param: None' == result.data

def test_rewrite_host_routing(client):
    result = client.get('/v1', headers={"Host": "www.mango.com"})
    assert b'This is V2' == result.data

def test_firewall_ip_reject(client):
    result = client.get('/', headers={"Host": "www.mango.com"}, environ_base={'REMOTE_ADDR': '10.192.0.1'})
    assert result.status_code == 403

def test_firewall_ip_accept(client):
    result = client.get('/', headers={"Host": "www.mango.com"}, environ_base={'REMOTE_ADDR': '55.55.55.55'})
    assert result.status_code == 200

def test_firewall_path_reject(client):
    result = client.get('/messages', headers={"Host": "www.mango.com"})
    assert result.status_code == 403

def test_firewall_path_accept(client):
    result = client.get('/pictures', headers={"Host": "www.mango.com"})
    assert result.status_code == 200

def test_host_routing_notfound(client):
    result = client.get('/', headers={"Host":"www.notmango.com"})
    assert b'Not Found' in result.data
    assert 404 == result.status_code

def test_server_bad_servers(client):
    result = client.get('/', headers={"Host":"www.apple.com"})
    assert b'This is the apple application. Serving on localhost:9082. Custom Header: None, Host Header: www.apple.com, Custom Param: None' == result.data

def test_server_no_servers(client):
    result = client.get('/', headers={"Host":"www.orange.com"})
    assert 503 == result.status_code

def test_path_routing_mango(client):
    result = client.get('/mango')
    assert re.match("This is the mango application. Serving on localhost:\d+. Custom Header: None, Host Header: localhost:\d+, Custom Param: None", result.data.decode('utf-8')) != None

def test_path_routing_apple(client):
    result = client.get('/apple')
    assert b'This is the apple application. Serving on localhost:9082. Custom Header: None, Host Header: localhost:9082, Custom Param: None' == result.data

def test_path_routing_notfound(client):
    result = client.get('/notmango')
    assert b'Not Found' in result.data
    assert 404 == result.status_code
