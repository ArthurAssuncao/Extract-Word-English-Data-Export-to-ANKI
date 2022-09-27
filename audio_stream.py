import os
import requests
import time
import shutil


class AudioStream:
    def __init__(self, session, headers):
        self.session = session
        self.headers = headers

    def audio_is_exists(self, file_path):
        if os.path.exists(file_path):
            return True
        return False

    def download_audio_file(self, url, file_path):
        # file_path = f'{type_data}/{name}'
        if not self.audio_is_exists(file_path):
            try:
                doc = self.session.get(url, headers=self.headers)
            except requests.exceptions.ConnectionError:
                time.sleep(30)
                try:
                    doc = self.session.get(url, headers=self.headers)
                except requests.exceptions.ConnectionError:
                    return False
            with open(file_path, 'wb') as f:
                f.write(doc.content)
        return True

    def copy_audio_files_to_anki_dir(self, source_path, destination_path):
        # source_path = f'{type_data}/{audio_name}'
        # destination_path = f'{ANKI_MEDIA_FILE_DIR}/{audio_name}'
        if (not self.audio_is_exists(destination_path)):
            shutil.copy(source_path, destination_path)
            return False
        return True
