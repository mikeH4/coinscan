class Index:
    def __init__(self,
        *,
        cols: list[str],
        unique: bool = False
    ):
        self.cols = cols
        self.unique = unique

    def gen_name(self, table: str):
        return f"idx_gener_{table}_" + "_".join(self.cols)

    def joined(self):
        return ','.join(self.cols)