import random
from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(0.1, 0.2)

    # @task
    # def login(self):
    #     self.client.post("http://127.0.0.1:8000/api/users/login", {"email": "abc@def.com", "password": "0000"})

    # def on_start(self):
    #     self.client.post("api/users/login", {"email": "abc@def.com", "password": "0000"})

    # @task
    # def newsfeeds(self):
    #     self.client.get('/api/posts', headers={'Authorization': 'token 29944cbaa794313c3435734c4b817ee364309ba7'})

    @task
    def locust_test(self):
        self.client.get('/api/users/locust_test')
