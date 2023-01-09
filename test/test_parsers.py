import time

import pytest

from parsers.CSVParser import CSVGrandParser
from parsers.ExcelParser import ExcelGrandParser


class ParserTests:
    @pytest.mark.parametrize("Parser,extension", [(ExcelGrandParser, "xlsx"), (CSVGrandParser, "csv")])
    def excel_parser_test(self, Parser, extension):
        start_time = time.time()
        parser = Parser(f"Optimized Kore.{extension}")
        occurrences = parser.get_occurrence_from_records(["jlpt_", "vocab_pos"])
        assert len(parser.all_records) == 6000
        assert len(occurrences) == 1
        assert time.time() - start_time < 3 * 60


