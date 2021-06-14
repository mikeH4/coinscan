class GeneralAddress:
    def __str__(self) -> str:
        return self.string_repr

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.string_repr}>"

    def __eq__(self, other):
        return str(self) == str(other)


class Address(GeneralAddress):
    def __init__(self,string_repr: str) -> None:
        string_repr = str(string_repr).lower()
        if len(string_repr) != 42:
            raise TypeError("Address must be of length 42")
        self.string_repr = string_repr

class BlockOrTransactionHash(GeneralAddress):
    def __init__(self,string_repr: str) -> None:
        string_repr = str(string_repr).lower()
        if len(string_repr) != 66:
            raise TypeError("BlockOrTransactionHash must be of length 66")
        self.string_repr = string_repr