from parsers.BaseParser import BaseParser
from utils.global_access_classes import Const, Config


# TODO finish it
class ApkgGrandParser(BaseParser):

    def remove_wrong_letters(self, word):
        for char in self.wrong_chars:
            word = word.replace(char, "_")
        return word.lower()

    def _get_numbers_for_headers(self, field_names):
        if hasattr(self.config, "interesting_columns") and self.config.interesting_columns is not None \
                and self.config.interesting_columns != ['']:
            for i, cell in enumerate(field_names):
                value = str(cell)
                if value in self.config.interesting_columns:
                    self.headers_to_numbers[self.remove_wrong_letters(value)] = i
        else:
            self.headers_to_numbers = {self.remove_wrong_letters(str(value)): i for i, value in enumerate(field_names)}
        self.headers = [(self.remove_wrong_letters(str(header)), str) for header in self.headers_to_numbers.keys()]

    def __init__(self, config: Config):
        super().__init__()
        self.headers_to_numbers = {}
        self.config = config
        self.dataset_name = config.absolute_path_to_file

    def _add_records(self, reader):
        records = []
        for row in reader:
            tab = (cell for i, cell in enumerate(row.values()) if i in self.headers_to_numbers.values())
            record = self.RecordClass(*tab)
            record.ID = next(Const.GRAND_ITER)
            records.append(record)
        return records
