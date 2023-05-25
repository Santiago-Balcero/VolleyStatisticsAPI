from locust import HttpUser, task


class GetPlayers(HttpUser):
    
    @task
    def get_players(self):
        self.client.get("/players")
