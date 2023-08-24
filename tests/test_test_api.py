import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_healthcheck():
    response = client.get('/test/healthcheck')
    print(response)
    assert response.status_code == 200

