class Address:
    def __init__(string_repr: str) -> None:
        if len(string_repr) != 42:
            raise TypeError("Address must be of length 42")
        self.string_repr = string_repr
    
    def __str__(self) -> str:
        return self.string_repr

    def __repr__(self) -> str:
        return f"<Address: {self.string_repr}>"