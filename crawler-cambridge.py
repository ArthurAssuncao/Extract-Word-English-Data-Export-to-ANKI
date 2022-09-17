
import csv
import requests
from fake_useragent import UserAgent
import re
import sys
import os
import shutil
from os.path import expanduser
from requests.adapters import HTTPAdapter, Retry
import time
import json
import os.path
from bs4 import BeautifulSoup

FILE_LIST = "{}-list-download.csv"
BACKUP_FILE = "{}-backup.json"
CAMBRIDGE_URL = "https://dictionary.cambridge.org/pronunciation/english/"
REGEX = re.compile(r'<span class="t tb fs16 hv1">us</span>.*'
                   r'<meta itemprop="contentURL" content="(https://dictionary.cambridge.org/media/english/.*.mp3)".*'
                   r'/<span class=[\'"]ipa dipa[\'"]>([^<>]*)</span>/', re.DOTALL)
REGEX_2 = re.compile(r'<span class="t tb fs16 hv1">us</span>.*'
                     r'<meta itemprop="contentURL" content="(https://dictionary.cambridge.org/media/english/.*.mp3)".*'
                     r'/<span class=[\'"]ipa dipa[\'"]>(.*)</span><div itemprop="description">/', re.DOTALL)

FILE_OUTPUT = "importacao-data-{}.csv"
ANKI_MEDIA_FILE_DIR = '~/.local/share/Anki2/User 1/collection.media'
HOME = expanduser("~")
ANKI_MEDIA_FILE_DIR = f'{HOME}/.local/share/Anki2/User 1/collection.media/'
ua = UserAgent()
HEADER = {'User-Agent': str(ua.chrome)}

type_data = sys.argv[1]
print("Tipo {}".format(type_data))

FILE_OUTPUT_HEADER = f"""
#separator:Semicolon
#html:false
#tags:{type_data}
#columns:Front Back Phonetic
#deck:ingles-vocabulario-comum
"""

RETRY_BACKOFF_FACTOR = 10


def reset_useragent():
    global ua
    global HEADER
    ua = UserAgent()
    HEADER = {'User-Agent': str(ua.chrome)}


def create_dir():
    try:
        os.mkdir(type_data)
    except FileExistsError:
        pass


def extract_ipa_audio_url(html):
    result = REGEX.findall(html)
    return {
        'success': len(result) > 0,
        'data': result[len(result) - 1] if len(result) > 0 else None
    }


def extract_ipa_audio_url_2(html):
    result = REGEX_2.findall(html)
    data = None
    if (len(result) > 0):
        data = result[len(result) - 1]
        data[1] = BeautifulSoup(data[1], "lxml").text

    return {
        'success': len(result) > 0,
        'data': data if len(result) > 0 else None
    }


def get_backup_downloaded(word):
    file_path = '{}/{}'.format(type_data, BACKUP_FILE.format(type_data))
    if not os.path.exists(file_path):
        return None
    data = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    if word in data:
        return data[word]
    return None


def save_backup_downloaded(word, result):
    file_path = '{}/{}'.format(type_data, BACKUP_FILE.format(type_data))
    data = {}
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    data[word] = result
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_ipa_audio(word):
    word.lower().replace("to-", "")
    backup = get_backup_downloaded(word)
    if backup:
        return backup
    url = CAMBRIDGE_URL + word
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=RETRY_BACKOFF_FACTOR)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    try:
        req = session.get(url, headers=HEADER)
    except requests.exceptions.ConnectionError:
        time.sleep(60)
        reset_useragent()
        req = session.get(url, headers=HEADER)
    result = extract_ipa_audio_url(req.text)
    if (not result['success']):
        result = extract_ipa_audio_url_2(req.text)
    if (result['success']):
        save_backup_downloaded(word, result)
    return result


def read_list():
    items = []
    file_list = '{}/{}'.format(type_data, FILE_LIST.format(type_data))
    with open(file_list, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        for row in spamreader:
            items.append((row[0], row[1]))
    return items


def save_csv_file(data):
    filename = FILE_OUTPUT.format(type_data)
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        f.write(FILE_OUTPUT_HEADER)
        writer = csv.writer(f, delimiter=';')

        writer.writerows(data)


def download_audio_file(url, name):
    file_path = f'{type_data}/{name}'
    if not os.path.exists(file_path):
        session = requests.Session()
        retry = Retry(connect=3, backoff_factor=RETRY_BACKOFF_FACTOR)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        try:
            doc = session.get(url, headers=HEADER)
        except requests.exceptions.ConnectionError:
            time.sleep(60)
            reset_useragent()
            doc = session.get(url, headers=HEADER)
        with open(file_path, 'wb') as f:
            f.write(doc.content)


def copy_audio_files_to_anki_dir(audio_name):
    source = f'{type_data}/{audio_name}'
    destination = f'{ANKI_MEDIA_FILE_DIR}/{audio_name}'
    if (not os.path.exists(destination)):
        shutil.copy(source, destination)


def generate_data_anki(items_pt_en):
    items = []
    counter = 0
    for item_pt_en in items_pt_en:
        word_pt = item_pt_en[0]
        word_en = item_pt_en[1]
        counter = counter + 1
        print(counter, word_pt, '=', word_en)
        word_fixed_to_cambrigde = word_en.replace(' ', '-').lower()
        result = get_ipa_audio(word_fixed_to_cambrigde)
        if (result['success']):
            audio_url = result['data'][0]
            ipa = result['data'][1]
            audio_name = audio_url[audio_url.rfind('/') + 1:]
            print(ipa, "\n")
            item = [f'{word_en} [sound:{audio_name}]', word_pt, f'/{ipa}/']
            # print(item)
            items.append(item)
            download_audio_file(audio_url, audio_name)
            copy_audio_files_to_anki_dir(audio_name)
        else:
            print(f"{word_pt} {word_en} Não encontrado")
            item = [word_pt, f'{word_en}', '']
    return items


def main():
    create_dir()

    items_pt_en = read_list()
    data_anki = generate_data_anki(items_pt_en)

    save_csv_file(data_anki)


if __name__ == "__main__":
    main()
