from pprint import pprint

import pytest
import server


class TestClient:
    @pytest.fixture()
    def test_client(self):
        server.app.testing = True
        server.competitions = server.load_competitions()
        server.clubs = server.load_clubs()
        with server.app.test_client() as client:
            return client

