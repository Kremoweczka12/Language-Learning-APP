import csv

from dataclasses import make_dataclass

from parsers.BaseParser import BaseParser
from utils.global_access_classes import Const, Config


class CSVGrandParser(BaseParser):

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

        with open(self.dataset_name, newline='', encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile)
            self._get_numbers_for_headers(reader.fieldnames)
            self.RecordClass = make_dataclass("Record", self.headers)  # , headers
            self.all_records = self._add_records(reader)

    def _add_records(self, reader):
        records = []
        for row in reader:
            tab = (cell for i, cell in enumerate(row.values()) if i in self.headers_to_numbers.values())
            record = self.RecordClass(*tab)
            record.ID = next(Const.GRAND_ITER)
            records.append(record)
        return records
