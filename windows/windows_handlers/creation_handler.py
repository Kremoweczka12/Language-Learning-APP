import json
from dataclasses import asdict

from PySide6 import QtWidgets
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QFileDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QLabel, QTableWidgetItem, QWidget
from playsound import playsound

from parsers.ApkgParser import ApkgGrandParser
from parsers.CSVParser import CSVGrandParser
from parsers.ExcelParser import ExcelGrandParser
from utils.CONSTANTS import StagesOrdering, UFTIcons
from utils.global_access_classes import Const, CurrentlyEdited, LeftMenuButton, Config
from windows.windows_handlers.base_handler import BaseHandler
import pandas as pd

from windows.windows_handlers.data_loading_handler import LoadedDataWindowHandler


class FirstViewWindowHandler(BaseHandler):
    @classmethod
    def initiate_task(cls):

        if hasattr(Const.main_window, "task_attributes") and Const.main_window.task_attributes is not []:
            try:
                cls.kill_exercise_task()
            except RuntimeError:
                print("already Deleted")

        Const.main_window.main_menu_box = QVBoxLayout(Const.main_window)
        Const.main_window.load_raw_button = LeftMenuButton("Load raw data", Const.main_window)
        Const.main_window.load_raw_button.clicked.connect(lambda: cls.load_config_or_raw_data(is_raw=True))
        Const.main_window.new_config_button = LeftMenuButton("New Configuration (pick CSV or Excel format)",
                                                             Const.main_window)
        Const.main_window.new_config_button.clicked.connect(lambda: cls.create_new_config())
        Const.main_window.load_config_button = LeftMenuButton("Load known config", Const.main_window)
        Const.main_window.load_config_button.clicked.connect(lambda: cls.load_config_or_raw_data(is_raw=False))
        Const.main_window.main_menu_box.addWidget(Const.main_window.load_raw_button, )
        Const.main_window.main_menu_box.addWidget(Const.main_window.load_config_button, )
        Const.main_window.main_menu_box.addWidget(Const.main_window.new_config_button, )
        if not hasattr(Const.main_window, "task_attributes"):
            Const.main_window.task_attributes = []
        #
        Const.main_window.task_attributes.extend(
            [Const.main_window.new_config_button, Const.main_window.load_config_button,
             Const.main_window.load_raw_button, Const.main_window.main_menu_box])
        Const.main_window.setCentralWidget(QWidget(Const.main_window))
        Const.main_window.centralWidget().setLayout(Const.main_window.main_menu_box)

    @classmethod
    def create_new_config(cls):
        try:
            playsound("sounds/regular_click.wav")
            path = QtWidgets.QFileDialog.getOpenFileName(Const.main_window,
                                                         'Hey! Select a File',
                                                         filter="data files (*.xlsx *.csv *.apkg)")[0]
            print(path)
            DataManagementView.initiate_task(path)
        except Exception as e:
            print(e)
            print("error")
            cls.kill_exercise_task()
            cls.initiate_task()

    @classmethod
    def reload_config_or_raw_data(cls, is_raw=False):
        path = Const.parser.config.json_file
        extensions_to_parsers = {"xlsx": ExcelGrandParser, "csv": CSVGrandParser, "apkg": ApkgGrandParser}
        try:
            playsound("sounds/regular_click.wav", False)
            if is_raw:

                configurations = {"absolute_path_to_file": path}
                parser = extensions_to_parsers[path.split(".")[-1]]

            else:

                with open(path, ) as json_file:
                    configurations = json.load(json_file)
                extension = configurations["absolute_path_to_file"].split(".")[-1]
                parser = extensions_to_parsers[extension]

        except ValueError:
            print(path)
            print("I CANT PARSE THIS FILE EXTENSION")
            return
        except KeyError:
            pass
            return

        if hasattr(Const.main_window, "task_attributes") and Const.main_window.task_attributes is not []:
            try:
                cls.kill_exercise_task(spare_loading_parts=True)
            except RuntimeError:
                print("already Deleted")
        try:
            parser = parser(Config(**configurations))
            Const.parser = parser

            LoadedDataWindowHandler.initiate_task(cls)
        except Exception as e:
            print(e)
            print("error")
            cls.kill_exercise_task()
            cls.initiate_task()

    @classmethod
    def load_config_or_raw_data(cls, is_raw: bool):
        extensions_to_parsers = {"xlsx": ExcelGrandParser, "csv": CSVGrandParser, "apkg": ApkgGrandParser}
        try:
            playsound("sounds/regular_click.wav", False)
            if is_raw:
                path = QtWidgets.QFileDialog.getOpenFileName(Const.main_window,
                                                             'Hey! Select a data File',
                                                             filter="data files (*.xlsx *.csv *.apkg)")[0]
                configurations = {"absolute_path_to_file": path}
                parser = extensions_to_parsers[path.split(".")[-1]]

            else:
                path = QtWidgets.QFileDialog.getOpenFileName(Const.main_window,
                                                             'Hey! Select a your config file',
                                                             filter="config files (*.json)")[0]

                with open(path, ) as json_file:
                    configurations = json.load(json_file)
                extension = configurations["absolute_path_to_file"].split(".")[-1]
                parser = extensions_to_parsers[extension]

        except ValueError:
            print("I CANT PARSE THIS FILE EXTENSION")
            return
        except KeyError:
            pass
            return
        # try to parse data with config

        if hasattr(Const.main_window, "task_attributes") and Const.main_window.task_attributes is not []:

            try:
                cls.kill_exercise_task()
            except RuntimeError:

                print("already Deleted")

        try:
            config = Config(**configurations)
            if path.endswith("json"):
                config.json_file = path
            parser = parser(config)
            Const.parser = parser
            LoadedDataWindowHandler.initiate_task(cls)
        except Exception as e:
            print(e)
            print("error")
            cls.kill_exercise_task()
            cls.initiate_task()


class DataManagementView(BaseHandler):
    @classmethod
    def fill_table_wth_excel(cls, excel_file_dir):
        extension = excel_file_dir.split(".")[-1]
        # cls.kill_exercise_task(main)
        try:
            Const.main_window.new_config_button.deleteLater()
            Const.main_window.load_config_button.deleteLater()
            Const.main_window.load_raw_button.deleteLater()
        except RuntimeError:
            print("already destroyed")
        tabs = pd.ExcelFile(excel_file_dir).sheet_names
        print(tabs)
        # add worksheet_choice
        df = pd.read_excel(excel_file_dir, tabs[0])
        if df.size == 0:
            return

        df.fillna('', inplace=True)
        Const.main_window.table.setRowCount(df.shape[0])
        Const.main_window.table.setColumnCount(df.shape[1])
        Const.main_window.table.setHorizontalHeaderLabels(df.columns)
        Const.main_window.loaded_excel_headers = list(df.columns)

        # returns pandas array object
        for row in df.iterrows():
            values = row[1]
            for col_index, value in enumerate(values):
                if isinstance(value, (float, int)):
                    value = '{0:0,.0f}'.format(value)
                tableItem = QTableWidgetItem(str(value))
                tableItem.setForeground(QBrush(QColor(255, 255, 255)))
                Const.main_window.table.setItem(row[0], col_index, tableItem)
        CurrentlyEdited.config_in_progress = Config()
        CurrentlyEdited.config_in_progress.file_name = excel_file_dir.split("/")[-1].replace(extension, "")
        CurrentlyEdited.config_in_progress.absolute_path_to_file = excel_file_dir

        # Const.main_window.table.setColumnWidth(2, 300)
        # Const.main_window.main_menu_box.addWidget(Const.main_window.table, 3)

    @classmethod
    def initiate_task(cls, filepath):

        Const.main_window.table = QTableWidget(Const.main_window)
        if not hasattr(Const.main_window, "task_attributes"):
            Const.main_window.task_attributes = []
        Const.main_window.task_attributes.extend([Const.main_window.table])
        # add mapping
        cls.fill_table_wth_excel(filepath)
        Const.main_window.configurations_data_box = QHBoxLayout(Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.configurations_data_box)
        Const.main_window.main_table_box = QVBoxLayout(Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.main_table_box)
        Const.main_window.main_table_box.addWidget(Const.main_window.table)
        Const.main_window.main_menu_box.addLayout(Const.main_window.main_table_box, 3)
        Const.main_window.main_menu_box.addLayout(Const.main_window.configurations_data_box, 1)
        Const.main_window.bottom_horizontal_box = QHBoxLayout(Const.main_window)
        Const.main_window.small_table = QTableWidget(Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.small_table)
        # Const.main_window.small_table.setHorizontalHeaderLabels(["native lang", "translation"])
        #
        Const.main_window.small_table.setRowCount(5)
        Const.main_window.small_table.setColumnCount(1)

        Const.main_window.small_table_box = QHBoxLayout(Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.small_table_box)
        Const.main_window.small_table_box.addWidget(Const.main_window.small_table)
        # choosen column label
        Const.main_window.chosen_label = QLabel(Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.chosen_label)
        Const.main_window.small_table_box.addWidget(Const.main_window.chosen_label)
        Const.main_window.chosen_label.setText("None")
        Const.main_window.chosen_label.hide()
        Const.main_window.configurations_current_info_box = QVBoxLayout(Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.configurations_current_info_box)
        Const.main_window.tool_tip = QLabel(Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.tool_tip)
        Const.main_window.tool_tip.setText(
            "(1/6) Pick columns that represent words (one word can have multiple representations)\n"
            "For example good choice would be columns where such a values occur:\n"
            " 'apple', 'ringo' , 'りんご' they all represent 'apple' in japanese.")

        # buttons label layout
        Const.main_window.buttons_in_info_layout_box = QHBoxLayout(Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.buttons_in_info_layout_box)
        Const.main_window.return_button = LeftMenuButton("Main menu", Const.main_window)
        Const.main_window.return_button.clicked.connect(lambda: cls.return_to_menu())
        Const.main_window.task_attributes.append(Const.main_window.return_button)
        Const.main_window.back_button = LeftMenuButton("Reverse Action", Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.back_button)
        Const.main_window.back_button.clicked.connect(lambda: cls.reverse_append_record())
        Const.main_window.add_record_button = LeftMenuButton("Add Selection", Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.add_record_button)
        Const.main_window.add_record_button.clicked.connect(lambda: cls.append_record())
        Const.main_window.next_button = LeftMenuButton(f"Next step {UFTIcons.RIGHT_ARROW}", Const.main_window)
        Const.main_window.task_attributes.append(Const.main_window.next_button)
        Const.main_window.next_button.clicked.connect(lambda: cls.append_to_config(2))
        Const.main_window.orientation_buttons = [Const.main_window.return_button, Const.main_window.add_record_button,
                                                 Const.main_window.back_button, Const.main_window.next_button]
        for button in Const.main_window.orientation_buttons:
            Const.main_window.buttons_in_info_layout_box.addWidget(button)
        Const.main_window.configurations_current_info_box.addWidget(Const.main_window.tool_tip)

        Const.main_window.configurations_current_info_box.addLayout(Const.main_window.buttons_in_info_layout_box)
        Const.main_window.configurations_data_box.addLayout(Const.main_window.small_table_box, 4)
        Const.main_window.configurations_data_box.addLayout(Const.main_window.configurations_current_info_box, 10)

    @classmethod
    def append_record(cls):
        playsound("sounds/regular_click.wav")
        indexes = Const.main_window.table.selectionModel().selectedColumns()
        for selections in Const.main_window.table.selectedRanges():
            Const.main_window.table.setRangeSelected(selections, False)
        indexes = [Const.main_window.loaded_excel_headers[index.column()] for index in indexes]
        if StagesOrdering.creation_position in StagesOrdering.single_choice_creation:
            Const.main_window.chosen_label.setText(indexes[0])
        else:
            for i, index in enumerate(indexes):
                tableItem = QTableWidgetItem(index)
                tableItem.setForeground(QBrush(QColor(255, 255, 255)))
                Const.main_window.small_table.insertRow(0)
                Const.main_window.small_table.setItem(0, 0, tableItem)
            for y in range(len(indexes)):
                Const.main_window.small_table.insertRow(Const.main_window.small_table.rowCount())

    @classmethod
    def reverse_append_record(cls):
        playsound("sounds/regular_click.wav")
        Const.main_window.small_table.removeRow(0)
        Const.main_window.small_table.insertRow(Const.main_window.small_table.rowCount())

    @classmethod
    def return_to_menu(cls):
        playsound("sounds/regular_click.wav")
        FirstViewWindowHandler.kill_exercise_task()
        FirstViewWindowHandler.initiate_task()

    @classmethod
    def append_to_config(cls, constrain: int):
        playsound("sounds/regular_click.wav")
        attribute = StagesOrdering.CONFIG_CREATION_STAGES[StagesOrdering.creation_position]

        # procesing current stage
        path = ""
        if StagesOrdering.creation_position in StagesOrdering.single_choice_creation:
            proper_items = ""
            setattr(CurrentlyEdited.config_in_progress, f"{attribute}_path", "")
            if Const.main_window.chosen_label.text() != "None":
                print(Const.main_window.loaded_excel_headers)
                if Const.main_window.chosen_label.text() not in Const.main_window.loaded_excel_headers:
                    print("It's not correct column name!")
                    return
                path = QtWidgets.QFileDialog.getExistingDirectory(Const.main_window,
                                                                  f'Hey! Select a select directory for {attribute} files', )

                if path == "":
                    print("its must be a currect path!")
                    return
                proper_items = Const.main_window.chosen_label.text()
                setattr(CurrentlyEdited.config_in_progress, f"{attribute}_path", path)
        else:
            proper_items = []
            for i in range(Const.main_window.small_table.rowCount()):
                item = Const.main_window.small_table.item(i, 0)
                if item and item.data(0) != "":
                    proper_items.append(item.data(0))
            # proper_items = [item.text() for item in Const.main_window.small_table.items(0) if item.text() != ""]
            list(set(proper_items))
            for item in proper_items:
                if item not in Const.main_window.loaded_excel_headers:
                    print(f"'{item}' is not proper column name!!")
                    return
            if len(proper_items) < constrain:
                print(f"There should be at least {constrain} columns selected!")
                return

        setattr(CurrentlyEdited.config_in_progress, attribute, proper_items)
        if StagesOrdering.creation_position == 5:
            if cls.save_created_json():
                FirstViewWindowHandler.initiate_task()
            return
        StagesOrdering.creation_position += 1
        Const.main_window.small_table.clearContents()
        Const.main_window.chosen_label.setText("None")
        description = StagesOrdering.CONFIG_CREATION_DESCRIPTIONS[StagesOrdering.creation_position]
        # going to the next stage
        if StagesOrdering.creation_position in StagesOrdering.single_choice_creation:
            Const.main_window.chosen_label.show()
            Const.main_window.small_table.hide()
            # Const.main_window.add_record_button.hide()
        else:
            Const.main_window.chosen_label.hide()
            Const.main_window.small_table.show()
            # Const.main_window.add_record_button.show()

        if StagesOrdering.creation_position == 5:
            Const.main_window.next_button.setText("Finish!")
            # Const.main_window.next_button.clicked.connect(lambda: cls.save_created_json(main))

        Const.main_window.tool_tip.setText(description)

    @classmethod
    def save_created_json(cls) -> bool:
        playsound("sounds/regular_click.wav")
        path = QFileDialog.getSaveFileName(
            Const.main_window, "Save configuration file", f"{CurrentlyEdited.config_in_progress.file_name}json",
            "JSON Files (*.json)")
        if path[0] == '':
            print("Its not correct file name or location!")
            return False
        config_file = {
            **{k: getattr(CurrentlyEdited.config_in_progress, k) for k in StagesOrdering.CONFIG_CREATION_STAGES},
            "words_sounds_path": CurrentlyEdited.config_in_progress.words_sounds_path,
            "sentences_sounds_path": CurrentlyEdited.config_in_progress.sentences_sounds_path,
            "images_path": CurrentlyEdited.config_in_progress.images_path,
            "absolute_path_to_file": CurrentlyEdited.config_in_progress.absolute_path_to_file}
        try:
            with open(path[0], "w") as out_file:
                json.dump(config_file, out_file, indent=4)
        except FileNotFoundError:
            print("No proper file location")
            return False
        return True
