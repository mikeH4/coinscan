from library.BaseSource import BaseSource

class IfConfig(BaseSource):
    url = "https://ifconfig.me/"

    def ip(self):
        res = self.request("/")
        return res.text