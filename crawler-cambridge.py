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

FILE_OUTPUT = "importacao-data-{}.csv"
ANKI_MEDIA_FILE_DIR = '~/.local/share/Anki2/User 1/collection.media'
HOME = expanduser("~")
ANKI_MEDIA_FILE_DIR = f'{HOME}/.local/share/Anki2/User 1/collection.media/'
ua = UserAgent()
HEADER = {'User-Agent': str(ua.chrome)}

type_data = sys.argv[1]
print("Tipo {}".format(type_data))

FILE_OUTPUT_HEADER = f"""
# separator:Semicolon
# html:false
# tags:{type_data}
# columns:Front Back Phonetic WordClass
# deck:ingles-vocabulario-comum
"""

RETRY_BACKOFF_FACTOR = 5


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


def locate_div_block(html, word):
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
        print(span_word_title_inside,
              span_language,
              span_ipa,
              span_us_block,
              audio)
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


def apply_regex(divs_block):
    results = []
    for div_block in divs_block:
        result = REGEX_WORD_TERMS.findall(div_block)
        if not result:
            # print(div_block)
            continue
        results.append(result[0])
    return results


def apply_regex_alt(divs_block):
    results = []
    for div_block in divs_block:
        result = REGEX_WORD_TERMS_ALT.findall(div_block)
        if not result:
            # print(div_block)
            continue
        results.append(result[0])
    return results


def apply_regex_without_class(divs_block):
    results = []
    for div_block in divs_block:
        result = REGEX_WORD_TERMS_WITHOUT_CLASS.findall(div_block)
        if not result:
            # print(div_block)
            pass
        results.append(result[0])
    return results


def apply_regex_uk(divs_block):
    results = []
    for div_block in divs_block:
        result = REGEX_WORD_TERMS_UK.findall(div_block)
        if not result:
            # print(div_block)
            continue
        results.append(result[0])
    return results


def is_idiom_block(html, word):
    soup_HTML = BeautifulSoup(html, 'html.parser')
    div = soup_HTML.find("div", attrs={"class": "idiom-block"})
    if (div is not None):
        span_word_title = div.find(["h2", "span"], attrs={"class": "headword"})
        span_word_title_text = span_word_title.text

        if (word.replace('-', ' ') in span_word_title_text):
            return True
    return False


def fill_result(results, indexes, has_word_class, word_was_changed):
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
        if (word_was_changed['change'] == WORD_CHANGES['ING_REMOVED']):
            ipas = [f'{ipa}iŋ' for ipa in ipas]
            word_classes = ['present participle']
        elif (word_was_changed['change'] == WORD_CHANGES['PLURAL_REMOVED']):
            word_classes = ['noun']
        elif (word_was_changed['change'] == WORD_CHANGES['SUPERLATIVE_REMOVED']):
            word_classes = ['adjetive', 'superlative']
        elif (word_was_changed['change'] == WORD_CHANGES['PAST_SUFFIX_REMOVED']):
            word_classes = ['past participle', 'past tense']
        elif (word_was_changed['change'] == WORD_CHANGES['ADJETIVE_SUFFIX_REMOVED']):
            word_classes = ['adjetive']
    data = {
        'word': main_result[0],
        'audio_url': '{}{}'.format(CAMBRIDGE_BASE_URL, main_result[indexes['audio_url']]),
        'ipa': ipas,
        'class': word_classes
    }
    return {
        'success': len(result) > 0,
        'data': data
    }


def replace_last_occurency(word, str_to_replace, replace_str):
    return replace_str.join(word.rsplit(str_to_replace, 1))


def extract_ipa_audio_url(html, word):
    divs_block = locate_div_block(html, word)
    is_idiom_word = False
    results = None

    word_was_changed = {
        'was_changed': False,
        'change': ''
    }
    if (len(divs_block) == 0):
        if (word.endswith('ing')):
            word_without_ing = replace_last_occurency(word, 'ing', '')
            divs_block = locate_div_block(html, word_without_ing)
            word_was_changed = {
                'was_changed': True,
                'change': WORD_CHANGES['ING_REMOVED']
            }
        elif (word.endswith('s')):
            word_without_s = replace_last_occurency(word, 's', '')
            divs_block = locate_div_block(html, word_without_s)
            word_was_changed = {
                'was_changed': True,
                'change': WORD_CHANGES['PLURAL_REMOVED']
            }
        elif (word.endswith('est')):
            word_without_est = replace_last_occurency(word, 'est', '')
            divs_block = locate_div_block(html, word_without_est)
            word_was_changed = {
                'was_changed': True,
                'change': WORD_CHANGES['SUPERLATIVE_REMOVED']
            }
        elif (word.endswith('ed')):
            word_without_est = replace_last_occurency(word, 'ed', '')
            divs_block = locate_div_block(html, word_without_est)
            word_was_changed = {
                'was_changed': True,
                'change': WORD_CHANGES['PAST_SUFFIX_REMOVED']
            }
        elif (word.endswith('er')):
            word_without_er = replace_last_occurency(word, 'er', 'e')
            divs_block = locate_div_block(html, word_without_er)
            word_was_changed = {
                'was_changed': True,
                'change': WORD_CHANGES['ADJETIVE_SUFFIX_REMOVED']
            }
    if (len(divs_block) == 0):
        is_idiom_word = is_idiom_block(html, word)
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
        results = apply_regex(divs_block)
    if (results is None or len(results) == 0):
        results = apply_regex_alt(divs_block)
    if (results is None or len(results) == 0):
        results = apply_regex_uk(divs_block)
        if (len(results) == 0):
            print(divs_block)

    has_word_class = True
    indexes = {
        'main': 0,
        'class': 1,
        'audio_url': 2,
        'ipa': 3
    }
    if (len(results) == 0):
        has_word_class = False
        results = apply_regex_without_class(divs_block)
        indexes = {
            'main': 0,
            'audio_url': 1,
            'ipa': 2
        }

    if len(results) > 0:
        if (not is_idiom_word):
            return fill_result(results, indexes, has_word_class, word_was_changed)
        if (is_idiom_word):
            return results
    return None


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
    if (word in MATCHING_WORDS):
        word = MATCHING_WORDS[word]
    backup = get_backup_downloaded(word)
    if backup:
        return backup
    url = CAMBRIDGE_DICT_URL.format(word)
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
    result = extract_ipa_audio_url(req.text, word)
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
        print(counter, word_pt, '=>', word_en)
        word_fixed_to_cambrigde = word_en.replace(' ', '-').replace("to-", "").lower()
        result = get_ipa_audio(word_fixed_to_cambrigde)
        if (result['success']):
            print(result, '\n')
            data = result['data']
            audio_url = data['audio_url']
            ipa = '/ /'.join(data['ipa']) if len(data['ipa']) > 1 else ''.join(data['ipa'])
            # ipa = ipa.replace(', ', '/ /')
            # ipa = ipa.split('/ /')
            # ipa = set(ipa)
            # ipa = list(ipa)
            # ipa = '/ /'.join(data['ipa']) if len(data['ipa']) > 1 else ''.join(data['ipa'])
            audio_name = audio_url[audio_url.rfind('/') + 1:]
            word_class = ', '.join(data['class']) if len(data['class']) > 1 else ''.join(data['class'])

            item = [f'{word_en}', word_pt, f'/{ipa}/', word_class]
            if (audio_url != ''):
                item = [f'{word_en} [sound:{audio_name}]', word_pt, f'/{ipa}/', word_class]
                download_audio_file(audio_url, audio_name)
                copy_audio_files_to_anki_dir(audio_name)
        else:
            print(f"{word_pt} {word_en} Não encontrado")
            item = [word_pt, f'{word_en}', '', '']
        items.append(item)
    return items


def main():
    create_dir()

    items_pt_en = read_list()
    data_anki = generate_data_anki(items_pt_en)

    save_csv_file(data_anki)


if __name__ == "__main__":
    main()
