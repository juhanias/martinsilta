import requests

class Foli:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "FöliPy/1.0.0 (python-requests/2.25.1)",
            "Accept": "application/json",
            "From": "juhani.astikainen@gmail.com",
        })
        self.cache = {}
        for category in self.get_categories():
            self.cache[category["category"]] = category["descr_fi"]

    def get_announcements(self):
        announcements = self.session.get("http://data.foli.fi/alerts").json()
        return announcements["global_message"], announcements["emergency_message"], announcements["messages"]

    def get_categories(self):
        return self.session.get("http://data.foli.fi/alerts/categories").json()
