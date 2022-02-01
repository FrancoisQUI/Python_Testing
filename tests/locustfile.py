from locust import HttpUser, task, between


class ClubWebUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.client.post("/showSummary", {
            "email": "test@test.fr",
        })

    @task
    def index(self):
        self.client.get("/book/Test_Competition/Test")

    @task
    def about(self):
        self.client.get("/")

    @task
    def logout(self):
        self.client.get('/logout')

    @task
    def purchase(self):
        self.client.post('/purchasePlaces', data={
            'places': 1,
            'competition': 'Test_Competition',
            'club': 'Test'
        })

    @task
    def display(self):
        self.client.get('/board')
