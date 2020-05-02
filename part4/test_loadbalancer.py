from loadbalancer import loadbalancer

import pytest
import re

@pytest.fixture
def client():
    with loadbalancer.test_client() as client:
        yield client

def test_host_routing_mango(client):
    result = client.get('/', headers={"Host":"www.mango.com"})
    assert re.match("This is the mango application. Serving on localhost:\d+.", result.data.decode('utf-8')) != None

def test_host_routing_apple(client):
    result = client.get('/', headers={"Host":"www.apple.com"})
    assert b'This is the apple application. Serving on localhost:9082.' == result.data

def test_host_routing_notfound(client):
    result = client.get('/', headers={"Host":"www.notmango.com"})
    assert b'Not Found' in result.data
    assert 404 == result.status_code

def test_server_bad_servers(client):
    result = client.get('/', headers={"Host":"www.apple.com"})
    assert b'This is the apple application. Serving on localhost:9082.' == result.data

def test_server_no_servers(client):
    result = client.get('/', headers={"Host":"www.orange.com"})
    assert 503 == result.status_code

def test_path_routing_mango(client):
    result = client.get('/mango')
    assert re.match("This is the mango application. Serving on localhost:\d+.", result.data.decode('utf-8')) != None

def test_path_routing_apple(client):
    result = client.get('/apple')
    assert b'This is the apple application. Serving on localhost:9082.' == result.data

def test_path_routing_notfound(client):
    result = client.get('/notmango')
    assert b'Not Found' in result.data
    assert 404 == result.status_code
