import requests
from .photo_details_pexels import Photo


class API:
    def __init__(self, PEXELS_API_KEY):
        self.PEXELS_AUTHORIZATION = {"Authorization": PEXELS_API_KEY}
        self.request = None
        self.json = None
        self.has_next_page = None
        self.next_page = None

    def get_entries(self):
        # Check if json data exists before trying to access it
        if self.json and "photos" in self.json:
            print(self.json)
            return [Photo(json_photo) for json_photo in self.json["photos"]]
        return None

    def search(self, query, results_per_page=15, page=1):
        query = query.replace(" ", "+")
        url = "https://api.pexels.com/v1/search?query={}&per_page={}&page={}".format(query, results_per_page, page)
        self.__request(url)

    def __request(self, url):
        try:
            self.request = requests.get(url, timeout=15, headers=self.PEXELS_AUTHORIZATION)
            print("send request process", self.request.status_code)

            if self.request.status_code == 200:
                self.json = self.request.json()
                self.has_next_page = "next_page" in self.json
                self.next_page = self.json.get("next_page")
            else:
                print(f"Request failed with status code: {self.request.status_code}")
                self.json = None
                self.has_next_page = False
                self.next_page = None

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Check your internet connection.")
            self.request = None
            self.json = None
            self.has_next_page = False
            self.next_page = None
            # Do not exit, allow the program to continue with an error state

    def search_next_page(self):
        if self.has_next_page:
            self.__request(self.next_page)
        else:
            return None
        return self.json
