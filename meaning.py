class Meaning:
    def __init__(self, definition, example, grammatical_class):
        self.definition = definition
        self.example = example.replace(';', ' /').replace(' ', '')
        self.grammatical_class = grammatical_class

    def to_dict(self):
        return {
            'definition': self.definition,
            'example': self.example,
            'grammatical_class': self.grammatical_class
        }
