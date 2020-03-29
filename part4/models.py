import requests

class Server:
    def __init__(self, endpoint, path="/healthcheck"):
        self.endpoint = endpoint
        self.path = path
        self.healthy = True
        self.timeout = 1
        self.scheme = "http://"

    def healthcheck_and_update_status(self):
        try:
            response = requests.get(self.scheme + self.endpoint + self.path, timeout=self.timeout)
            if response.ok:
                self.mark_as_up()
            else:
                self.mark_as_down()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            self.mark_as_down()

    def mark_as_down(self):
        self.healthy = False

    def mark_as_up(self):
        self.healthy = True

    def __repr__(self):
        return "<Server: {} {} {}>".format(self.endpoint, self.healthy, self.timeout)
