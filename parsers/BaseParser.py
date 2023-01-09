import itertools
from dataclasses import asdict

from utils.global_access_classes import Const


class BaseParser:
    wrong_chars = ["/", " ", "-"]

    def put_space_bars(self, word):
        return word.replace("<b>", " ").replace("</b>", " ")

    def remove_wrong_letters(self, word):
        for char in self.wrong_chars:
            word = word.replace(char, "_")

        return word.lower()

    def __init__(self):
        Const.GRAND_ITER = itertools.count()
        self.headers = []
        self.all_records = []

    def filter_records(self, tab=None, **kwargs):
        if not tab:
            filtered_records = self.all_records
        else:
            filtered_records = tab

        try:
            limit_to = kwargs.pop("limit_to")
        except KeyError:
            limit_to = len(filtered_records)
        try:
            limit_from = kwargs.pop("limit_from") - 1
        except KeyError:
            limit_from = 0

        for key, value in kwargs.items():
            if isinstance(value, list):
                filtered_records = [rc for rc in filtered_records if getattr(rc, key) in value]
            else:
                filtered_records = [rc for rc in filtered_records if getattr(rc, key) == value]
        if limit_to or limit_from:
            filtered_records = filtered_records[limit_from:limit_to]

        return filtered_records

    def filter_records_by_string(self, tab=None, text_value=None):
        value_from_record = lambda r: str(r.ID) + "".join([f"_{str(value)}" for value in asdict(r).values()])
        if text_value:
            if not tab:
                filtered_tab = self.all_records
            else:
                filtered_tab = tab
            return [record for record in filtered_tab if text_value in value_from_record(record)]
        return self.all_records

    def get_occurrence_from_records(self, headers=None, tab_of_records=None):
        if not headers:
            headers = [self.remove_wrong_letters(header[0]) for header in self.headers]
        if not tab_of_records:
            tab_of_records = self.all_records
        all_occurrences = {h: {} for h in headers}
        for record in tab_of_records:
            for header in headers:
                value = getattr(record, header)
                if value in all_occurrences[header]:
                    all_occurrences[header][value] += 1
                else:
                    all_occurrences[header][value] = 1
        return all_occurrences
