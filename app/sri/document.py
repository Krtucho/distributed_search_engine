class Document:
    def __init__(self, freq: int, tf: float, w: float):
        super().__init__()

        self.freq = freq
        self.tf = tf
        self.w = w
