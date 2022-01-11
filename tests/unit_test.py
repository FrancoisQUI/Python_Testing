from pprint import pprint

import pytest
import server


class TestClient:
    @pytest.fixture()
    def test_client(self):
        server.app.testing = True
        server.competitions = [
            {
                "name": "Spring Festival",
                "date": "2020-03-27 10:00:00",
                "numberOfPlaces": "25"
            },
            {
                "name": "Fall Classic",
                "date": "2020-10-22 13:30:00",
                "numberOfPlaces": "13"
            }
        ]
        server.clubs = [
            {
                "name": "Gooduser",
                "email": "good@email.com",
                "points": "13"
            },
            {
                "name": "anotheruser",
                "email": "another@email.com",
                "points": "2"
            }
        ]

        with server.app.test_client() as client:
            yield client


class TestIndex(TestClient):
    def test_index_should_have_response_code_200(self, test_client):
        res = test_client.get("/")
        assert res.status_code == 200

    def test_index_use_index_template(self, test_client):
        res = test_client.get("/")
        assert str(res.data).find("Welcome to the GUDLFT Registration Portal!") > 0


class TestShowSummary(TestClient):
    def test_should_have_response_code_200(self, test_client):
        res = test_client.post("/showSummary", data={'email': 'good@email.com'})
        assert res.status_code == 200

    def test_bad_email_should_have_response_code_301(self, test_client):
        res = test_client.post("/showSummary", data={'email': 'bad@email.com'})
        assert res.status_code == 301

    def test_no_email_should_have_response_code_301(self, test_client):
        res = test_client.post("/showSummary", data={'email': ''})
        assert res.status_code == 301



