import os


class Phonetic:
    def __init__(self, ipa, audio_url, dialect=None):
        self.ipa = ipa
        self.audio_url = audio_url
        self.audio_name = os.path.basename(audio_url)
        dot_index = self.audio_name.rfind('.')
        dash_index = self.audio_name.rfind('-')
        self.dialect = dialect
        if (dialect is None):
            self.dialect = self.audio_name[dash_index + 1:dot_index]

    def to_dict(self):
        return {
            'ipa': self.ipa,
            'audio_url': self.audio_url,
            'audio_name': self.audio_name,
            'dialect': self.dialect
        }
