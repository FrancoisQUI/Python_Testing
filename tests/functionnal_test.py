from pprint import pprint

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By


server_url = "http://127.0.0.1:5000/"

#  restart server before test : use the base JSON file
#  fixture for Firefox
@pytest.fixture(scope="class")
def driver_init(request):
    ff_driver = webdriver.Firefox()
    request.cls.driver = ff_driver
    yield
    ff_driver.close()


@pytest.mark.usefixtures("driver_init")
class BasicTest:
    def connect_user(self, email):
        email_field = self.driver.find_element(By.NAME, 'email')
        button = self.driver.find_element(By.XPATH, '/html/body/form/button')
        email_field.send_keys(email)
        button.click()


@pytest.mark.usefixtures("driver_init")
class TestGUDLFTAsClub(BasicTest):
    def test_user_can_access_main_page(self):
        self.driver.get(server_url)
        assert "GUDLFT Registration" in self.driver.title

    def test_club_can_login(self):
        self.driver.get(f"{server_url}")
        self.connect_user("john@simplylift.co")
        assert 'Summary | GUDLFT Registration' in self.driver.title

    def test_club_can_book_places_and_places_are_deducted(self):
        self.driver.get(server_url)
        self.connect_user("john@simplylift.co")
        #  Book places for "Test test 2" event
        self.driver.find_element(By.XPATH, "/html/body/ul/li[4]/a").click()
        assert 'Booking for Test test 2 || GUDLFT' in self.driver.title
        #  Book 3 places
        self.driver.find_element(By.NAME, "places").send_keys("3")
        self.driver.find_element(By.XPATH, '/html/body/form/button').click()
        assert self.driver.current_url == f"{server_url}purchasePlaces"
        assert 'Points available: 4' in self.driver.find_element(By.ID, 'points').text
        assert 'Number of Places: 22' in self.driver.find_element(By.XPATH, '//*[@id="Testtest2"]').text
