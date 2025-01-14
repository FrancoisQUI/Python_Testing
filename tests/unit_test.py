import flask
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
                "numberOfPlaces": 25,
                "placeValue": 1,
                "over": True
            },
            {
                "name": "Fall Classic",
                "date": "2020-10-22 13:30:00",
                "numberOfPlaces": 13,
                "placeValue": 1,
                "over": True
            },
            {
                "name": "Future Competition",
                "date": "3000-10-22 13:30:00",
                "numberOfPlaces": 3,
                "placeValue": 1,
                "over": False
            },
            {
                "name": "Future Competition 2",
                "date": "3000-10-22 13:30:00",
                "numberOfPlaces": 20,
                "placeValue": 1,
                "over": False
            },
            {
                "name": "Over Competition",
                "date": "1999-10-22 13:30:00",
                "numberOfPlaces": 18,
                "placeValue": 1,
                "over": True
            }
        ]
        server.clubs = [
            {
                "name": "Gooduser",
                "email": "good@email.com",
                "points": 13
            },
            {
                "name": "anotheruser",
                "email": "another@email.com",
                "points": 2
            }
        ]

        server.MAX_PLACE_PER_CLUB = 12

        with server.app.test_client() as client:
            yield client


def flash_message_content_is(message):
    return str(flask.get_flashed_messages()).find(message) > 0


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

    def test_over_competition_should_show_book_link(self, test_client):
        competition_selector = "OverCompetition"  # CSS selector is competition name without spaces
        response = test_client.post("/showSummary", data={'email': 'good@email.com'})
        response_content = bs(response.data, 'html.parser')
        assert str(response_content.select(f"#{competition_selector}")). \
                   find("<a class=\"book_link\"") <= 0

    def test_not_over_competition_should_not_show_book_link(self, test_client):
        competition_selector = "FutureCompetition"  # CSS selector is competition name without spaces
        response = test_client.post("/showSummary", data={'email': 'good@email.com'})
        response_content = bs(response.data, 'html.parser')
        assert str(response_content.select(f"#{competition_selector}")). \
                   find("<a class=\"book_link\"") > 0


class TestBook(TestClient):
    def test_not_over_competition_should_have_response_code_200(self, test_client):
        club_name = "Gooduser"
        competition_name = "Future Competition"
        response = test_client.get(f"/book/{competition_name}/{club_name}")
        assert response.status_code == 200

    def test_over_competition_should_have_response_code_403(self, test_client):
        club_name = "Gooduser"
        competition_name = "Over Competition"
        response = test_client.get(f"/book/{competition_name}/{club_name}")
        assert response.status_code == 403


class TestPurchasePlaces(TestClient):
    def test_user_have_enough_point_to_purchase_places_should_have_response_code_200(self, test_client):
        club_name = "Gooduser"
        competition_name = "Future Competition"
        required_places = 3
        response = test_client.post("/purchasePlaces", data={'club': club_name,
                                                             'competition': competition_name,
                                                             'places': required_places})
        assert response.status_code == 200
        assert flash_message_content_is('Great-booking complete!')

    def test_user_have_not_enough_point_to_purchase_places_should_have_response_code_403(self, test_client):
        club_name = "Gooduser"
        competition_name = "Future Competition"
        required_places = 99
        response = test_client.post("/purchasePlaces", data={'club': club_name,
                                                             'competition': competition_name,
                                                             'places': required_places})
        assert response.status_code == 403
        assert flash_message_content_is('Not enough points')

    def test_user_claim_more_place_than_competition_available_places_should_have_response_code_403(self, test_client):
        club_name = "Gooduser"
        competition_name = "Future Competition"
        required_places = 11
        response = test_client.post("/purchasePlaces", data={'club': club_name,
                                                             'competition': competition_name,
                                                             'places': required_places})
        assert response.status_code == 403
        assert flash_message_content_is("Not enough place for this competition")

    def test_user_claim_more_than_authorized_place_should_have_response_code_403(self, test_client):
        club_name = "Gooduser"
        competition_name = "Future Competition 2"
        required_places = 13
        response = test_client.post("/purchasePlaces", data={'club': club_name,
                                                             'competition': competition_name,
                                                             'places': required_places})
        assert response.status_code == 403
        assert flash_message_content_is(f"Only {server.MAX_PLACE_PER_CLUB} places per club allowed")


class TestDisplayBoard(TestClient):
    def test_display_board_should_have_response_200(self, test_client):
        response = test_client.get("/board")
        assert response.status_code == 200


class TestLogout(TestClient):
    def test_logout_should_have_code_200(self, test_client):
        response = test_client.get("/logout")
        assert response.status_code == 200
