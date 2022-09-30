from meaning import Meaning
from phonetic import Phonetic


class WordInfo:
    def __init__(self, word, translation_pt, main_phonetic, grammatical_classes, phonetics, synonyms, antonyms, meanings):
        self.word = word
        self.translation_pt = translation_pt.replace(' /', ',')
        self.main_phonetic = main_phonetic
        self.grammatical_classes = list(set(grammatical_classes))
        self.phonetics = phonetics
        self.synonyms = list(set(synonyms))
        self.antonyms = list(set(antonyms))
        self.meanings = meanings

        self.fix_phonetics()

    def fix_phonetics(self):
        if (self.main_phonetic != ''):
            self.main_phonetic = f'/{self.main_phonetic.replace("/", "")}/'
        new_phonetics = []
        for phonetic in self.phonetics:
            new_phonetic = phonetic
            phonetic_ipa = phonetic['ipa'].replace("/", "")
            if (phonetic_ipa != ''):
                new_phonetic['ipa'] = f'/{phonetic_ipa}/'
                new_phonetics.append(new_phonetic)
        self.phonetics = new_phonetics

    def to_dict(self):
        return {
            'word': self.word,
            'translation_pt': self.translation_pt,
            'main_phonetic': self.main_phonetic,
            'grammatical_classes': self.grammatical_classes,
            'phonetics': self.phonetics,
            'synonyms': self.synonyms,
            'antonyms': self.antonyms,
            'meanings': self.meanings
        }

    def main_audio_file(self, main_dialect='us'):
        if (len(self.phonetics) == 0):
            return {
                'audio_url': '',
                'audio_name': '',
                'dialect': ''
            }
        for phonetic in self.phonetics:
            if (phonetic['dialect'] == main_dialect):
                return {
                    'audio_url': phonetic['audio_url'],
                    'audio_name': phonetic['audio_name'],
                    'dialect': phonetic['dialect']
                }
        for phonetic in self.phonetics:
            if (phonetic['audio_url'] != ''):
                return {
                    'audio_url': phonetic['audio_url'],
                    'audio_name': phonetic['audio_name'],
                    'dialect': phonetic['dialect']
                }

        return {
            'audio_url': self.phonetics[0]['audio_url'],
            'audio_name': self.phonetics[0]['audio_name'],
            'dialect': self.phonetics[0]['dialect']
        }

    def phonetics_to_str(self):
        phonetics = set()
        for phonetic in self.phonetics:
            phonetics.add(phonetic['ipa'])
        phonetics.add(self.main_phonetic)
        phonetics_list = list(phonetics)
        phonetics_list = list(filter(None, phonetics_list))
        if (len(phonetics_list) == 0):
            return ''
        if (len(phonetics_list) == 1):
            return phonetics_list[0]
        return ', '.join(phonetics_list)

    def grammatical_classes_to_str(self):
        grammatical_classes = set()
        for grammatical_class in self.grammatical_classes:
            grammatical_classes.add(grammatical_class)
        grammatical_classes_list = list(grammatical_classes)
        if (len(grammatical_classes_list) == 1):
            return grammatical_classes_list[0]
        return ', '.join(grammatical_classes_list)

    def synonyms_to_str(self):
        synonyms = set()
        for synonym in self.synonyms:
            synonyms.add(synonym)
        synonyms_list = list(synonyms)
        if (len(synonyms_list) == 1):
            return synonyms_list[0]
        return ', '.join(synonyms_list)

    def antonyms_to_str(self):
        antonyms = set()
        for antonym in self.antonyms:
            antonyms.add(antonym)
        antonyms_list = list(antonyms)
        if (len(antonyms_list) == 1):
            return antonyms_list[0]
        return ', '.join(antonyms_list)

    def wrapper_word(self, text_to_wrap, word_to_wrap):
        word = word_to_wrap.lower()
        text = text_to_wrap.lower()
        words_text = text.split(" ")
        wrapper_words = []
        for word_text in words_text:
            new_word = word_text.lower()
            if (word_text.replace(".", '').replace("!", '').replace("?", '').replace(",", '') == word):
                new_word = new_word.replace(word, f"<span class='word-in-example'>{word_to_wrap}</span>")
            wrapper_words.append(new_word)
        new_text = ' '.join(wrapper_words)
        new_text = new_text.capitalize()
        return new_text

    def meanings_to_str(self, word):
        meanings = set()
        for meaning in self.meanings:
            example = meaning['example']
            if (example != ''):
                example = self.wrapper_word(example, word)
                meanings.add(f"{meaning['grammatical_class']}: {example}")
        meanings_list = list(meanings)
        if (len(meanings_list) == 0):
            return ''
        if (len(meanings_list) == 1):
            return meanings_list[0]
        meanings_list_wrapper_imperfect = "</p><p class='example'>".join(meanings_list)
        return f"<p class='example'>{meanings_list_wrapper_imperfect}</p>"

    def to_str(self):
        word = self.word.replace('-', ' ').capitalize()
        audio_file = self.main_audio_file()['audio_name']
        phonetics = self.phonetics_to_str()
        grammatical_classes = self.grammatical_classes_to_str()
        synonyms = self.synonyms_to_str()
        antonyms = self.antonyms_to_str()
        meanings = self.meanings_to_str(word)
        return f'{word} [sound:{audio_file}];{self.translation_pt};{phonetics};{grammatical_classes};{synonyms};{antonyms};{meanings}'

    @classmethod
    def from_json_response(cls, response_json, translation_pt):
        word = response_json['word']
        main_phonetic = ''
        if 'phonetic' in response_json:
            main_phonetic = response_json['phonetic']
        else:
            print("main phonetic: campo não encontrado")

        grammatical_classes = []

        phonetics = []
        for phonetic_json in response_json['phonetics']:
            phonetic_text = phonetic_json['text'] if 'text' in phonetic_json else ''
            phonetic = Phonetic(phonetic_text, phonetic_json['audio']).to_dict()
            if (phonetic_text == ''):
                print('phonetic text: campo não encontrado')
            phonetics.append(phonetic)

        synonyms = []
        antonyms = []
        meanings = []
        for meaning_json in response_json['meanings']:
            grammatical_class = meaning_json['partOfSpeech']
            if (grammatical_class not in grammatical_classes):
                grammatical_classes.append(grammatical_class)
            if 'synonyms' in meaning_json:
                synonyms.extend(meaning_json['synonyms'])
            if 'antonyms' in meaning_json:
                antonyms.extend(meaning_json['antonyms'])
            for definition in meaning_json['definitions']:
                example = definition['example'] if 'example' in definition else ''
                meaning = Meaning(definition['definition'], example, grammatical_class).to_dict()
                meanings.append(meaning)
                if 'synonyms' in definition:
                    synonyms.extend(definition['synonyms'])
                if 'antonyms' in definition:
                    antonyms.extend(definition['antonyms'])

        return cls(word, translation_pt, main_phonetic, grammatical_classes, phonetics, synonyms, antonyms, meanings)

    @classmethod
    def from_dict(cls, dictionary):
        return cls(dictionary['word'], dictionary['translation_pt'], dictionary['main_phonetic'],
                   dictionary['grammatical_classes'], dictionary['phonetics'],
                   dictionary['synonyms'], dictionary['antonyms'], dictionary['meanings'])

    @classmethod
    def join_words(cls, words_info):
        if (len(words_info) == 1):
            return words_info[0]
        main_word = words_info[0]
        for i in range(1, len(words_info)):
            other_word = words_info[i]
            if (main_word.word.replace('-', ' ') != other_word.word.replace('-', ' ')):
                continue
            for grammatical_class in other_word.grammatical_classes:
                if grammatical_class not in main_word.grammatical_classes:
                    main_word.grammatical_classes.append(grammatical_class)
            for phonetic in other_word.phonetics:
                if phonetic not in main_word.phonetics:
                    main_word.phonetics.append(phonetic)
            for synonym in other_word.synonyms:
                if synonym not in main_word.synonyms:
                    main_word.synonyms.append(synonym)
            for antonym in other_word.antonyms:
                if antonym not in main_word.antonyms:
                    main_word.antonyms.append(antonym)
            for meaning in other_word.meanings:
                if meaning not in main_word.meanings:
                    main_word.meanings.append(meaning)
        return main_word
