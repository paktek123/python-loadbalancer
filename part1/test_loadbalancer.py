from loadbalancer import loadbalancer

import pytest

@pytest.fixture
def client():
    with loadbalancer.test_client() as client:
        yield client

def test_not_found(client):
    result = client.get('/')
    assert b'hello' in result.data
