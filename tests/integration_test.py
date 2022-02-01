from pprint import pprint

import flask
from bs4 import BeautifulSoup as bs

import pytest
import server


class TestClient:
    @pytest.fixture()
    def test_client(self):
        with server.app.test_client() as client:
            return client


def flash_message_content_is(message):
    return str(flask.get_flashed_messages()).find(message) > 0


class TestIntegration(TestClient):

    def test_club_can_login_and_is_redirected_on_logout(self, test_client):
        login_page = test_client.get("/")
        can_login = test_client.get("/", data={'email': 'john@simplylift.co'})
        can_logout = test_client.get("/logout")

        login_page_content = bs(login_page.data, features="html.parser")

        assert login_page.status_code == 200
        assert u"<title>GUDLFT Registration</title>" in \
               str(login_page_content.select("Title"))
        assert can_login.status_code == 200
        assert can_logout.status_code == 200

    def test_logged_club_with_enough_points_can_book_places_clubs_points_reflected(self, test_client):
        club = server.clubs[3]
        competition = server.competitions[4]
        places_to_book = 1
        #  Connect club
        test_client.get("/", data={'email': club['email']})
        test_client.get("/showSummary")
        #  Show book screen
        book_screen = test_client.get(f"/book/{competition['name']}/{club['name']}")
        club_points_before_booking = server.clubs[3]["points"]
        #  Book competition
        booking = test_client.post(f'/purchasePlaces', data={
            'places': places_to_book,
            'club': club['name'],
            'competition': competition['name']
        }, follow_redirects=True)
        club_points_after_booking = server.clubs[3]["points"]

        assert book_screen.status_code == 200
        assert booking.status_code == 200
        assert club_points_after_booking == \
               club_points_before_booking - places_to_book * competition["placeValue"]

    def test_logged_club_with_not_enough_points_can_t_book_places(self, test_client):
        club = server.clubs[4]
        competition = server.competitions[4]
        places_to_book = 2
        #  Connect club
        test_client.get("/", data={'email': club['email']})
        test_client.get("/showSummary")
        #  Show book screen
        book_screen = test_client.get(f"/book/{competition['name']}/{club['name']}")
        #  Book competition
        booking = test_client.post(f'/purchasePlaces', data={
            'places': places_to_book,
            'club': club['name'],
            'competition': competition['name']
        }, follow_redirects=True)

        assert book_screen.status_code == 200
        assert booking.status_code == 403

    def test_logged_club_with_enough_points_can_book_places_competition_places_reflected(self, test_client):
        club = server.clubs[3]
        competition = server.competitions[4]
        places_to_book = 1
        #  Connect club
        test_client.get("/", data={'email': club['email']})
        test_client.get("/showSummary")
        #  Show book screen
        book_screen = test_client.get(f"/book/{competition['name']}/{club['name']}")
        competition_place_before_booking = server.competitions[4]["numberOfPlaces"]
        #  Book competition
        booking = test_client.post(f'/purchasePlaces', data={
            'places': places_to_book,
            'club': club['name'],
            'competition': competition['name']
        }, follow_redirects=True)
        competition_place_after_booking = server.competitions[4]["numberOfPlaces"]

        assert book_screen.status_code == 200
        assert booking.status_code == 200
        assert competition_place_after_booking == \
               competition_place_before_booking - places_to_book
