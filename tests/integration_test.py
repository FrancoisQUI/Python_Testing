import pytest
import server


class TestClient:
    @pytest.fixture()
    def test_client(self):
        with server.app.test_client() as client:
            return client


class TestIntegration(TestClient):

    def test_client_can_login_and_is_redirected_on_logout(self, test_client):
        login_page = test_client.get("/")
        can_login = test_client.get("/", data={'email': 'john@simplylift.co'})
        can_logout = test_client.get("/logout")

        assert login_page.status_code == 200
        assert can_login.status_code == 200
        assert can_logout.status_code == 200
