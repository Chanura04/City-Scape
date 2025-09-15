class Photo:
    def __init__(self, json_photo):
        self.__photo = json_photo

    def url(self):
        return self.__photo["src"]["original"]
    def img_name(self):
        return self.__photo["alt"]
