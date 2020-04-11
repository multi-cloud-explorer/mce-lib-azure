import pytest
import os
import json

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
FIXTURES_DIR = os.path.join(CURRENT_DIR, 'fixtures')

@pytest.fixture
def fixtures_dir():
    return FIXTURES_DIR

@pytest.fixture
def json_file(fixtures_dir):

    def _loader(filename, mode='r'):
        path = os.path.join(fixtures_dir, filename)
        if mode == 'r':
            with open(path, mode) as fp:
                return json.load(fp)
        else:
            with open(path, 'rb') as fp:
                return fp.read()

    return _loader

class MockResponse:
    """
    from unittest.mock import patch

    def test_mytest(mock_response_class):

        with patch("requests.get") as func:
            func.return_value = mock_response_class(200, {"ping": "pong"})
            response = requests.get('http://localhost/ping')
            assert response.status_code == 200
            assert response.json() == {"ping": "pong"}

        with patch("requests.get") as func:
            func.return_value = mock_response_class(500, {}, raise_error=True, reason="server error")
            response = requests.get('http://localhost/ping')
            assert response.status_code == 500
            assert response.json() == {}
    """
    
    def __init__(self, status_code, content, raise_error=None, reason=None, headers={}):
        self.status_code = status_code
        self.content = content
        self.raise_error = raise_error
        self.reason = reason
        self.headers = headers

    def json(self):
        return self.content

    def raise_for_status(self):
        if self.raise_error:
            raise Exception(self.reason)

    def get_reason(self):
        return self.reason or self.content
         
    text = property(fget=get_reason)

@pytest.fixture(scope="session")
def mock_response_class():
    return MockResponse

