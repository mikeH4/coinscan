from library.BaseSource import BaseSource

class IfConfig(BaseSource):
    url = "https://ifconfig.me/"

    def get(self):
        res = self.request("/ip")
        return res.text

class Google(BaseSource):
    url = "https://google.com/"

    def get(self):
        res = self.request("/")
        return res.text