import csv

from word_en_pt import WordEnPt


class CSVStream:
    def __init__(self, words_list_path, words_list_output, file_output_header):
        self.words_list_path = words_list_path
        self.words_list_output = words_list_output
        self.file_output_header = file_output_header

    def read_list(self):
        words = []
        # words_list = '{}/{}'.format(type_data, words_list.format(type_data))
        with open(self.words_list_path, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';')
            for row in spamreader:
                word = WordEnPt(row[0], row[1])
                words.append(word)
        return words

    def save_csv_file(self, data):
        # words_list_output = FILE_OUTPUT.format(type_data)
        with open(self.words_list_output, 'w', encoding='UTF8', newline='') as f:
            f.write(self.file_output_header)
            writer = csv.writer(f, delimiter=';')

            writer.writerows(data)
