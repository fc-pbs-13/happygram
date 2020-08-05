import random
from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(5, 9)

    @task
    def login(self):
        self.client.post("http://127.0.0.1:8000/api/users/login", {"email": "abc@def.com", "password": "0000"})


    @task
    def newsfeeds(self):
        self.client.get('/posts', headers={'Authorization': 'token 29944cbaa794313c3435734c4b817ee364309ba7'})
