from core.Token import Token

class TokenSearch:
    def __init__(self, search) -> None:
        results = db.find(search)

        self.results = [Token.from_row(row) for row in results]