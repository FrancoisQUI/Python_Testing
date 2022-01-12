from pprint import pprint
from bs4 import BeautifulSoup as bs

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
                "numberOfPlaces": "25",
                "over": True
            },
            {
                "name": "Fall Classic",
                "date": "2020-10-22 13:30:00",
                "numberOfPlaces": "13",
                "over": True
            },
            {
                "name": "Future Competition",
                "date": "3000-10-22 13:30:00",
                "numberOfPlaces": "18",
                "over": False
            },
            {
                "name": "Over Competition",
                "date": "3000-10-22 13:30:00",
                "numberOfPlaces": "18",
                "over": True
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
        response = test_client.get("/")
        assert response.status_code == 200

    def test_index_use_index_template(self, test_client):
        response = test_client.get("/")
        assert str(response.data).find("Welcome to the GUDLFT Registration Portal!") > 0


class TestShowSummary(TestClient):
    def test_should_have_response_code_200(self, test_client):
        response = test_client.post("/showSummary", data={'email': 'good@email.com'})
        assert response.status_code == 200

    def test_bad_email_should_have_response_code_301(self, test_client):
        response = test_client.post("/showSummary", data={'email': 'bad@email.com'})
        assert response.status_code == 301

    def test_no_email_should_have_response_code_301(self, test_client):
        response = test_client.post("/showSummary", data={'email': ''})
        assert response.status_code == 301

    def test_competition_show_book_link_if_not_over(self, test_client):
        competition = "FutureCompetition"  # CSS selector is competition name without spaces
        response = test_client.post("/showSummary", data={'email': 'good@email.com'})
        response_content = bs(response.data, 'html.parser')
        assert str(response_content.select(f"#{competition}")).find("<a class=\"book_link\"")

    def test_competition_not_show_book_link_if_over(self, test_client):
        competition = "OverCompetition"  # CSS selector is competition name without spaces
        response = test_client.post("/showSummary", data={'email': 'good@email.com'})
        response_content = bs(response.data, 'html.parser')
        assert str(response_content.select(f"#{competition}")).find("<a class=\"book_link\"") < 0