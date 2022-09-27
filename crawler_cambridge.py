import re
import requests
from requests.adapters import HTTPAdapter, Retry
import time
from bs4 import BeautifulSoup

from audio_stream import AudioStream
from word_info import WordInfo
from phonetic import Phonetic


class CrawlerCambridge:
    CAMBRIDGE_BASE_URL = 'https://dictionary.cambridge.org'
    CAMBRIDGE_DICT_URL = CAMBRIDGE_BASE_URL + "/dictionary/english/{}"
    REGEXES = {
        'word': r'<span class=[\'"]hw dhw[\'"]>([a-zA-Z\- ,\'\.]*)</span>.*',
        'class': r'<span class=[\'"]pos dpos[\'"] title=[\'"][a-zA-Z, \.\'-]*[\'"]>([a-zA-Z ,]*)</span>.*',
        'slang': r'<span class=[\'"]region dreg[\'"]>us</span>.*',
        'audio_url': r'<source src=[\'"](/media/english/us_pron/[a-zA-Z0-9_\-\./]*\.mp3)[\'"] type=[\'"]audio/mpeg[\'"]/>.*',
        'ipa': r'/<span class=[\'"]ipa dipa lpr-2 lpl-1[\'"]>(.*)</span>/',
        'slang_uk': r'<span class=[\'"]region dreg[\'"]>uk</span>.*',
        'audio_url_uk': r'<source src=[\'"](/media/english/uk_pron/[a-zA-Z0-9_\-\./]*\.mp3)[\'"] type=[\'"]audio/mpeg[\'"]/>.*',
        'word_alt': r'<span class=[\'"]headword[\'"]><b>([a-zA-Z\- ,\'\.]*)</b></span>.*',
    }

    REGEX_WORD_TERMS = re.compile(REGEXES['word'] + REGEXES['class'] + REGEXES['slang'] + REGEXES['audio_url'] + REGEXES['ipa'], re.DOTALL)

    REGEX_WORD_TERMS_ALT = re.compile(REGEXES['word_alt'] + REGEXES['class'] + REGEXES['slang'] + REGEXES['audio_url'] + REGEXES['ipa'], re.DOTALL)

    REGEX_WORD_TERMS_UK = re.compile(REGEXES['word'] + REGEXES['class'] + REGEXES['slang_uk'] + REGEXES['audio_url_uk'] + REGEXES['ipa'], re.DOTALL)

    REGEX_WORD_TERMS_WITHOUT_CLASS = re.compile(REGEXES['word'] + REGEXES['slang'] + REGEXES['audio_url'] + REGEXES['ipa'], re.DOTALL)

    WORD_CHANGES = {
        'ING_REMOVED': 'ing removed',
        'PLURAL_REMOVED': 'plural removed',
        'SUPERLATIVE_REMOVED': 'superlative removed',
        'PAST_SUFFIX_REMOVED': 'past suffix removed',
        'ADJETIVE_SUFFIX_REMOVED': 'adjetive suffix removed'
    }

    MATCHING_WORDS = {
        'okay': 'ok',
        'e-mail': 'email',
        'fewer': 'few',
        'vs': 'versus',
        'criteria': 'criterion',
        'ie': 'i.e.',
        'faster': 'fast'
    }

    def __init__(self, retry_factor, req_headers, audio_word_path, anki_media_file_dir):
        self.retry_factor = retry_factor
        self.req_headers = req_headers
        self.session = None
        self.audio_downloader = AudioStream(self.session, self.req_headers)
        self.audio_word_path = audio_word_path
        self.anki_media_file_dir = anki_media_file_dir
        self.dialect = 'us'

        self.set_session()

    def set_session(self):
        self.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=self.retry_factor)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def extract_from_cambridge(self, wordEnPT):
        word_en = wordEnPT.word_en
        word_pt = wordEnPT.word_pt
        word_fixed_to_cambrigde = word_en.replace(' ', '-').replace("to-", "").lower()
        result = self.get_ipa_audio(word_fixed_to_cambrigde)
        item = None
        if (result['success']):
            print(result, '\n')
            data = result['data']
            audio_url = data['audio_url']
            ipa = data['ipa']
            ipa = [Phonetic(item, audio_url, self.dialect).to_dict() for item in ipa]
            # audio_name = audio_url[audio_url.rfind('/') + 1:]
            word_class = data['class']

            main_phonetic = ''
            if (len(ipa) > 0):
                main_phonetic = ipa[0]['ipa']
            item = WordInfo(word_en, word_pt, main_phonetic, word_class, ipa, [], [], [])
            # if (audio_url != ''):
            #     audio_path = self.audio_word_path.format(audio_name)
            #     if (not self.audio_downloader.audio_is_exists(audio_path)):
            #         url = audio_url
            #         self.audio_downloader.download_audio_file(url, audio_path)
            #     destination_path = self.anki_media_file_dir + audio_name
            #     if (not self.audio_downloader.audio_is_exists(destination_path)):
            #         self.audio_downloader.copy_audio_files_to_anki_dir(audio_path, destination_path)
        else:
            print(f"{word_pt} {word_en} Não encontrado")
            item = None
        return item

    def locate_div_block(self, html, word):
        soup_HTML = BeautifulSoup(html, 'html.parser')
        divs_will_remove = soup_HTML.findAll('span', attrs={'class': 'irreg-infls'})
        [div_will_remove.decompose() for div_will_remove in divs_will_remove]
        divs_will_remove = soup_HTML.findAll('span', attrs={'class': 'pv-body dpv-body'})
        [div_will_remove.decompose() for div_will_remove in divs_will_remove]

        divs = soup_HTML.findAll("div", attrs={"class": ["pos-header dpos-h", "pv-block"]})

        result = []
        for div in divs:

            span_word_title = div.find(["h2", "span"], attrs={"class": "headword"})
            span_word_title_inside = None
            if (span_word_title is not None):
                span_word_title_inside = span_word_title.find("span", attrs={"class": 'hw dhw'})
                if (span_word_title_inside is None):
                    span_word_title_inside = span_word_title.find("b")
            else:
                span_word_title = div.find(["h2", "span"], attrs={"class": "hw dhw"})
                span_word_title_inside = span_word_title
            # span_word_class = div.find("span", attrs={"class": 'pos dpos'})

            span_us_block = div.find(["span", 'div'], attrs={"class": 'us dpron-i'})
            span_language = None
            span_ipa = None
            audio = None
            if (span_us_block is not None):
                span_language = span_us_block.find("span", attrs={"class": 'region dreg'})
                span_ipa = span_us_block.find("span", attrs={"class": 'ipa dipa lpr-2 lpl-1'})
                audio = span_us_block.find("source", attrs={"type": 'audio/mpeg'})
            if (span_ipa is None or audio is None):
                span_uk_block = div.find(["span", 'div'], attrs={"class": 'uk dpron-i'})
                if (span_uk_block is not None):
                    span_language = span_uk_block.find("span", attrs={"class": 'region dreg'})
                    span_ipa = span_uk_block.find("span", attrs={"class": 'ipa dipa lpr-2 lpl-1'})
                    audio = span_uk_block.find("source", attrs={"type": 'audio/mpeg'})
                    self.dialect = 'uk'
            # print(span_word_title_inside, span_language, span_ipa, span_us_block, audio)
            if span_word_title is None or \
                    span_word_title_inside is None or \
                    span_language is None or \
                    span_ipa is None or \
                    span_us_block is None or\
                    audio is None:
                continue
            span_word_title_text = span_word_title.text.lower()
            if (word in span_word_title_text
                or word.replace('-', ' ') in span_word_title_text
                or word in span_word_title_text.replace('something ', '').replace('someone/something', '')
                    or word.replace('-', ' ') in span_word_title_text.replace('something ', '').replace('someone/something', '')):
                result.append(str(div))
        return result

    def apply_regex(self, divs_block):
        results = []
        for div_block in divs_block:
            result = self.REGEX_WORD_TERMS.findall(div_block)
            if not result:
                # print(div_block)
                continue
            results.append(result[0])
        return results

    def apply_regex_alt(self, divs_block):
        results = []
        for div_block in divs_block:
            result = self.REGEX_WORD_TERMS_ALT.findall(div_block)
            if not result:
                # print(div_block)
                continue
            results.append(result[0])
        return results

    def apply_regex_without_class(self, divs_block):
        results = []
        for div_block in divs_block:
            result = self.REGEX_WORD_TERMS_WITHOUT_CLASS.findall(div_block)
            if not result:
                # print(div_block)
                pass
            results.append(result[0])
        return results

    def apply_regex_uk(self, divs_block):
        results = []
        for div_block in divs_block:
            result = self.REGEX_WORD_TERMS_UK.findall(div_block)
            if not result:
                # print(div_block)
                continue
            results.append(result[0])
        return results

    def is_idiom_block(self, html, word):
        soup_HTML = BeautifulSoup(html, 'html.parser')
        div = soup_HTML.find("div", attrs={"class": "idiom-block"})
        if (div is not None):
            span_word_title = div.find(["h2", "span"], attrs={"class": "headword"})
            span_word_title_text = span_word_title.text

            if (word.replace('-', ' ') in span_word_title_text):
                return True
        return False

    def fill_result(self, results, indexes, has_word_class, word_was_changed):
        main_result = results[indexes['main']]
        word_classes = set()
        ipas = set()
        for result in results:
            ipa_text = BeautifulSoup(result[indexes['ipa']], "lxml").text

            ipa_list = ipa_text.split(', ')
            ipa_set = set(ipa_list)
            ipas = ipas | ipa_set
            if (has_word_class):
                word_class = result[indexes['class']].split(',')
                word_class = [word.strip() for word in word_class]
                word_classes.update(word_class)
        ipas = list(ipas)
        word_classes = list(word_classes)
        if (word_was_changed['was_changed']):
            if (word_was_changed['change'] == self.WORD_CHANGES['ING_REMOVED']):
                ipas = [f'{ipa}iŋ' for ipa in ipas]
                word_classes = ['present participle']
            elif (word_was_changed['change'] == self.WORD_CHANGES['PLURAL_REMOVED']):
                word_classes = ['noun']
            elif (word_was_changed['change'] == self.WORD_CHANGES['SUPERLATIVE_REMOVED']):
                word_classes = ['adjetive', 'superlative']
            elif (word_was_changed['change'] == self.WORD_CHANGES['PAST_SUFFIX_REMOVED']):
                word_classes = ['past participle', 'past tense']
            elif (word_was_changed['change'] == self.WORD_CHANGES['ADJETIVE_SUFFIX_REMOVED']):
                word_classes = ['adjetive']
        data = {
            'word': main_result[0],
            'audio_url': '{}{}'.format(self.CAMBRIDGE_BASE_URL, main_result[indexes['audio_url']]),
            'ipa': ipas,
            'class': word_classes
        }
        return {
            'success': len(result) > 0,
            'data': data
        }

    def replace_last_occurency(self, word, str_to_replace, replace_str):
        return replace_str.join(word.rsplit(str_to_replace, 1))

    def extract_ipa_audio_url(self, html, word):
        divs_block = self.locate_div_block(html, word)
        is_idiom_word = False
        results = None

        word_was_changed = {
            'was_changed': False,
            'change': ''
        }
        if (len(divs_block) == 0):
            if (word.endswith('ing')):
                word_without_ing = self.replace_last_occurency(word, 'ing', '')
                divs_block = self.locate_div_block(html, word_without_ing)
                word_was_changed = {
                    'was_changed': True,
                    'change': self.WORD_CHANGES['ING_REMOVED']
                }
            elif (word.endswith('s')):
                word_without_s = self.replace_last_occurency(word, 's', '')
                divs_block = self.locate_div_block(html, word_without_s)
                word_was_changed = {
                    'was_changed': True,
                    'change': self.WORD_CHANGES['PLURAL_REMOVED']
                }
            elif (word.endswith('est')):
                word_without_est = self.replace_last_occurency(word, 'est', '')
                divs_block = self.locate_div_block(html, word_without_est)
                word_was_changed = {
                    'was_changed': True,
                    'change': self.WORD_CHANGES['SUPERLATIVE_REMOVED']
                }
            elif (word.endswith('ed')):
                word_without_est = self.replace_last_occurency(word, 'ed', '')
                divs_block = self.locate_div_block(html, word_without_est)
                word_was_changed = {
                    'was_changed': True,
                    'change': self.WORD_CHANGES['PAST_SUFFIX_REMOVED']
                }
            elif (word.endswith('er')):
                word_without_er = self.replace_last_occurency(word, 'er', 'e')
                divs_block = self.locate_div_block(html, word_without_er)
                word_was_changed = {
                    'was_changed': True,
                    'change': self.WORD_CHANGES['ADJETIVE_SUFFIX_REMOVED']
                }
        if (len(divs_block) == 0):
            is_idiom_word = self.is_idiom_block(html, word)
            results = {
                'success': True,
                'data': {
                    'word': word,
                    'audio_url': '',
                    'ipa': '',
                    'class': ['idiom phrase']
                }
            }
        if (not is_idiom_word and len(divs_block) == 0):
            raise ValueError('Não encontrou nenhuma parte do html compatível. Arrumar código')
        if (results is None):
            results = self.apply_regex(divs_block)
        if (results is None or len(results) == 0):
            results = self.apply_regex_alt(divs_block)
        if (results is None or len(results) == 0):
            results = self.apply_regex_uk(divs_block)
            self.dialect = 'uk'
            if (len(results) == 0):
                # print(divs_block)
                pass

        has_word_class = True
        indexes = {
            'main': 0,
            'class': 1,
            'audio_url': 2,
            'ipa': 3
        }
        if (len(results) == 0):
            has_word_class = False
            results = self.apply_regex_without_class(divs_block)
            indexes = {
                'main': 0,
                'audio_url': 1,
                'ipa': 2
            }

        if len(results) > 0:
            if (not is_idiom_word):
                return self.fill_result(results, indexes, has_word_class, word_was_changed)
            if (is_idiom_word):
                return results
        return None

    def get_ipa_audio(self, word):
        if (word in self.MATCHING_WORDS):
            word = self.MATCHING_WORDS[word]
        url = self.CAMBRIDGE_DICT_URL.format(word)
        print(url)
        try:
            req = self.session.get(url, headers=self.req_headers)
        except requests.exceptions.ConnectionError:
            time.sleep(30)
            req = self.session.get(url, headers=self.req_headers)
        result = self.extract_ipa_audio_url(req.text, word)
        return result
