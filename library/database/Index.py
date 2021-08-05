class Index:
    cols: list[str]
    unique: bool

    def __init__(self,
        *,
        cols: list[str],
        unique: bool = False
    ):
        self.cols = cols
        self.unique = unique

    def gen_name(self, table: str):
        uniq = "uniq_" if self.unique else ""
        return f"idx_gener_{table}_{uniq}" + "_".join(self.cols)

    def joined(self):
        return ','.join(self.cols)