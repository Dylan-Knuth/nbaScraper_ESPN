import time


class RequestTracker:
    def __init__(self):
        self.requests = []

    def add_request(self):
        current_time = time.time()
        # Remove timestamps older than 60 seconds
        self.requests = [req for req in self.requests if current_time - req < 60]
        # Add the current request timestamp
        self.requests.append(current_time)

    def get_requests_per_minute(self):
        # The length of the requests list gives the count of requests in the last minute
        return len(self.requests)