from library.BaseSource import BaseSource, TorRequestPool

class IfConfig(BaseSource):
    url = "https://ifconfig.me/"

    request_manager = TorRequestPool

    def get(self):
        res = self.request("/ip")
        return res.text

class Google(BaseSource):
    url = "https://google.com/"

    def get(self):
        res = self.request("/")
        return res.text