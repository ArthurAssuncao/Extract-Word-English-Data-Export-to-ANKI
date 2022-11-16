import sys
import csv
import json
import random

# palavra_som
# traducão
# pronuncia
# classe
# sinonimo
# antonimo
# frases

TYPE_DATA = sys.argv[1]

WORDS_DIR = f'../{TYPE_DATA}'
WORDS_LIST = f"{WORDS_DIR}/{TYPE_DATA}.csv"

FILE_OUTPUT = f"../anki-import-{TYPE_DATA}.csv"

FILE_OUTPUT_HEADER = f"""\
# separator:Semicolon
# html:true
# tags:{TYPE_DATA}
# columns:Front Back Phonetic GrammaticalClasses Synonyms Antonyms Meanings
# deck:english-{TYPE_DATA}
"""

FILE_CONFIG = f"{WORDS_DIR}/{TYPE_DATA}.json"

SORT_LIST = True


def read_config():
    with open(FILE_CONFIG) as f_config:
        data = json.load(f_config)
        return data
    return None


def read_list():
    data = []
    words_list_path = WORDS_LIST
    with open(words_list_path, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        for row in spamreader:
            data.append(row)
    return data


def save_csv_file(data):
    words_list_output = FILE_OUTPUT.format(TYPE_DATA)
    with open(words_list_output, 'w', encoding='UTF8', newline='') as f:
        f.write(FILE_OUTPUT_HEADER)
        writer = csv.writer(f, delimiter=';')

        writer.writerows(data)
    return True


def generate_new_data(data, corresp_dict):
    new_data = []
    for value in data:
        new_value = []
        keys = corresp_dict.keys()
        for key in keys:
            corresp_dict_value = corresp_dict[key]
            if corresp_dict_value is not None:
                new_value.append(value[corresp_dict_value])
            else:
                new_value.append('')
        new_data.append(new_value)
    return new_data


def sort_random_list(data):
    new_data = data
    if (SORT_LIST):
        random.shuffle(new_data)
    return new_data


def main():
    print("Tipo {}".format(TYPE_DATA))

    config_data = read_config()

    data = read_list()

    data = generate_new_data(data, config_data)

    data = sort_random_list(data)

    save_csv_file(data)

    print("finished")


if __name__ == "__main__":
    main()
