class WordEnPt:
    def __init__(self, word_en, word_pt):
        self.word_en = word_en
        self.word_pt = word_pt

    def __str__(self):
        return f'{self.word_en}; {self.word_pt}'
