import os
import json
from word_info import WordInfo


class Backuper:
    def __init__(self, type_data, backup_file_path):
        self.type_data = type_data
        self.backup_file_path = backup_file_path

    def get_backup_downloaded(self, word):
        # file_path = '{}/{}'.format(type_data, BACKUP_FILE.format(type_data))
        if not os.path.exists(self.backup_file_path):
            return None
        data = {}
        with open(self.backup_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        if word in data:
            return WordInfo.from_dict(data[word])
        return None

    def save_backup_downloaded(self, word, result):
        # file_path = '{}/{}'.format(type_data, BACKUP_FILE.format(type_data))
        data = {}
        if os.path.exists(self.backup_file_path):
            with open(self.backup_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        data[word] = result.to_dict()
        with open(self.backup_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
