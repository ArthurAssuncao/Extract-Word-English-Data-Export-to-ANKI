

from os.path import expanduser
import requests
from fake_useragent import UserAgent
import sys
import os
from requests.adapters import HTTPAdapter, Retry
import time

import json


from word_info import WordInfo
from backuper import Backuper
from audio_stream import AudioStream
from csv_stream import CSVStream
from crawler_cambridge import CrawlerCambridge


API_DICTIONARY = 'https://api.dictionaryapi.dev/api/v2/entries/en/{}'

ANKI_MEDIA_FILE_DIR = '~/.local/share/Anki2/User 1/collection.media'
HOME = expanduser("~")

RETRY_BACKOFF_FACTOR = 5

TYPE_DATA = sys.argv[1]

FILE_OUTPUT_HEADER = f"""\
# separator:Semicolon
# html:false
# tags:{TYPE_DATA}
# columns:Front Back Phonetic GrammaticalClasses Synonyms Antonyms Meanings
# deck:english-{TYPE_DATA}
"""

WORDS_DIR = f'../{TYPE_DATA}'
AUDIO_WORD_PATH = f'{WORDS_DIR}/' + '{}'
WORDS_LIST = f"{WORDS_DIR}/{TYPE_DATA}.csv"
BACKUP_FILE = f"{WORDS_DIR}/{TYPE_DATA}-backup.json"
FILE_OUTPUT = f"../anki-import-{TYPE_DATA}.csv"
ANKI_MEDIA_FILE_DIR = '~/.local/share/Anki2/User 1/collection.media'
HOME = expanduser("~")
ANKI_MEDIA_FILE_DIR = f'{HOME}/.local/share/Anki2/User 1/collection.media/'


class CrawlerEnglishWords:
    def __init__(self, type_data, file_input, file_output, file_output_header, backup_file_path, anki_media_file_dir, retry_factor, api_dictionary):
        self.type_data = type_data
        self.file_input = file_input
        self.file_output = file_output
        self.file_output_header = file_output_header
        self.anki_media_file_dir = anki_media_file_dir
        self.backup_file_path = backup_file_path
        self.retry_factor = retry_factor
        self.api_dictionary = api_dictionary
        self.req_headers = None
        self.session = None
        self.words = None

        self.set_useragent()
        self.set_session()

        self.create_dir()

        self.csv_stream = CSVStream(self.file_input, self.file_output, self.file_output_header)
        self.audio_downloader = AudioStream(self.session, self.req_headers)

        self.backuper = Backuper(self.type_data, self.backup_file_path)

        self.words = self.csv_stream.read_list()

        self.cambridge_crawler = CrawlerCambridge(self.retry_factor, self.req_headers, AUDIO_WORD_PATH, ANKI_MEDIA_FILE_DIR)

    def request_word(self, word):
        word = word.lower().replace(' ', '-')
        url = self.api_dictionary.format(word)
        print(url)
        try:
            req = self.session.get(url, headers=self.req_headers)
        except requests.exceptions.ConnectionError:
            time.sleep(30)
            self.reset_useragent()
            req = self.session.get(url, headers=self.req_headers)
        return req

    def request_by_other_crawler(self, wordEnPT):
        return self.cambridge_crawler.extract_from_cambridge(wordEnPT)

    def is_word_incomplete(self, word_info):
        without_phonetic = True
        for phonetic in word_info.phonetics:
            if (phonetic['ipa'] != ''):
                without_phonetic = False

        return without_phonetic

    def get_words_info(self):
        words = []
        counter = 0
        for word in self.words:
            is_used_other_crawler = False
            counter = counter + 1
            word_en = word.word_en
            word_pt = word.word_pt
            print(counter, word_en, word_pt)
            word_in_backup = self.backuper.get_backup_downloaded(word_en)
            word_info = word_in_backup
            if (word_in_backup is None):
                response = self.request_word(word.word_en)
                response_text = response.text
                response_json_list = json.loads(response_text)
                if (response.status_code != 200 or ('title' in response_json_list and response_json_list.title != 'No Definitions Found')):
                    print(word_en, 'Não encontrada')
                    word_info = self.request_by_other_crawler(word)
                    is_used_other_crawler = True
                    if (word_info is None):
                        continue

                if (is_used_other_crawler is False):
                    words_info = []
                    for response_json in response_json_list:
                        word_info = WordInfo.from_json_response(response_json, word_pt)
                        words_info.append(word_info)
                    word_info = WordInfo.join_words(words_info)
                    if (self.is_word_incomplete(word_info)):
                        new_word_info = self.request_by_other_crawler(word)
                        words_info = [word_info, new_word_info]
                        word_info = WordInfo.join_words(words_info)
            for phonetic in word_info.phonetics:
                if (phonetic['audio_url'] is not None):
                    audio_path = AUDIO_WORD_PATH.format(phonetic['audio_name'])
                    if (not self.audio_downloader.audio_is_exists(audio_path)):
                        url = phonetic['audio_url']
                        self.audio_downloader.download_audio_file(url, audio_path)
                    destination_path = ANKI_MEDIA_FILE_DIR + phonetic['audio_name']
                    if (not self.audio_downloader.audio_is_exists(destination_path)):
                        self.audio_downloader.copy_audio_files_to_anki_dir(audio_path, destination_path)
            if (word_in_backup is None):
                self.backuper.save_backup_downloaded(word_info.word.replace('-', ' '), word_info)
            words.append(word_info.to_str().split(';'))
        self.csv_stream.save_csv_file(words)

    def set_session(self):
        self.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=self.retry_factor)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        # try:
        #     req = session.get(url, headers=HEADER)
        # except requests.exceptions.ConnectionError:
        #     time.sleep(60)
        #     reset_useragent()
        #     req = session.get(url, headers=HEADER)

    def create_dir(self):
        try:
            os.mkdir(self.type_data)
        except FileExistsError:
            pass

    def set_useragent(self):
        ua = UserAgent(verify_ssl=False)
        self.req_headers = {'User-Agent': str(ua.chrome)}


def main():
    print("Tipo {}".format(TYPE_DATA))

    crawler = CrawlerEnglishWords(TYPE_DATA, WORDS_LIST, FILE_OUTPUT, FILE_OUTPUT_HEADER, BACKUP_FILE,
                                  ANKI_MEDIA_FILE_DIR, RETRY_BACKOFF_FACTOR, API_DICTIONARY)
    crawler.get_words_info()


if __name__ == "__main__":
    main()
