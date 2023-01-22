import json
from dataclasses import asdict

from PySide6 import QtCore, QtGui
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QSizePolicy, QLineEdit, QCheckBox, \
    QListWidget, QHBoxLayout, QWidget, QRadioButton, QLabel, QSpinBox, QPushButton, QListView
from playsound import playsound

from error_handling.basic_error_window import display_error_window
from utils.CONSTANTS import UFTIcons
from utils.global_access_classes import Const, BasicMenuButton, ErrorDialog
from windows.windows_handlers.base_handler import BaseHandler


class LoadedDataWindowHandler(BaseHandler):
    @classmethod
    def initiate_task(cls, main_menu_view_handler):

        try:

            Const.main_window.new_config_button.deleteLater()
            Const.main_window.load_config_button.deleteLater()
            Const.main_window.load_raw_button.deleteLater()
        except RuntimeError:
            print("already destroyed")

        Const.main_window.currently_used_records = Const.parser.all_records
        Const.main_window.all_selected_records = []
        Const.main_window.preview_table = QTableWidget(Const.main_window)

        Const.main_window.task_attributes.append(Const.main_window.preview_table)

        cls.show_me_all()
        Const.main_window.preview_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        Const.main_window.data_box = QVBoxLayout(Const.main_window)

        Const.main_window.preview_table.setGeometry(0, 0, 650, 350)

        # show_all_button
        Const.main_window.show_all_button = BasicMenuButton("Display All", Const.main_window)
        Const.main_window.show_all_button.setGeometry(10, 360, 160, 60)
        Const.main_window.show_all_button.clicked.connect(lambda: cls.show_me_all())

        # show_only_selected
        Const.main_window.show_only_selected = BasicMenuButton("Show all selected", Const.main_window)
        Const.main_window.show_only_selected.setGeometry(180, 360, 160, 60)
        Const.main_window.show_only_selected.clicked.connect(lambda: cls.show_only_selected(selected=True))

        # show_only_deselected
        Const.main_window.show_only_deselected = BasicMenuButton("Show all deselected", Const.main_window)
        Const.main_window.show_only_deselected.setGeometry(350, 360, 160, 60)
        Const.main_window.show_only_deselected.clicked.connect(lambda: cls.show_only_selected(selected=False))

        # select_all_displayed
        Const.main_window.select_displayed = BasicMenuButton("Select displayed", Const.main_window)
        Const.main_window.select_displayed.setGeometry(10, 430, 160, 60)
        Const.main_window.select_displayed.clicked.connect(lambda: cls.select_all_in_current_view())

        # deselect_all_displayed
        Const.main_window.deselect_displayed = BasicMenuButton("Deselect displayed", Const.main_window)
        Const.main_window.deselect_displayed.setGeometry(180, 430, 160, 60)
        Const.main_window.deselect_displayed.clicked.connect(lambda: cls.select_all_in_current_view(deselect=True))

        Const.main_window.data_box.addWidget(Const.main_window.show_all_button)
        Const.main_window.data_box.addWidget(Const.main_window.show_only_selected)
        Const.main_window.data_box.addWidget(Const.main_window.show_only_deselected)
        Const.main_window.data_box.addWidget(Const.main_window.select_displayed)
        Const.main_window.data_box.addWidget(Const.main_window.deselect_displayed)

        # dropdownlist

        Const.main_window.filter_list_widget = QListWidget(Const.main_window)
        filter_by = [header[0] for header in Const.parser.headers]
        if Const.parser.config.filters_columns:
            filter_by = Const.parser.config.filters_columns

        Const.main_window.filter_list_widget.insertItem(0, "NONE")
        for number, header in enumerate(filter_by):
            Const.main_window.filter_list_widget.insertItem(number + 1, header)

        size = 10 * (len(filter_by)) + 5
        if size > 200:
            size = 200
        else:
            size += 30

        # not displaying
        Const.main_window.filter_list_widget.setGeometry(700, 120, 160, size)
        Const.main_window.filter_list_widget.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.filter_list_widget.setCurrentRow(0)
        Const.main_window.filter_list_widget.itemClicked.connect(lambda: cls.fill_filter_preview_table())
        Const.main_window.data_box.addWidget(Const.main_window.filter_list_widget)
        size += 130
        Const.main_window.filter_preview_table = QTableWidget(Const.main_window)
        Const.main_window.filter_preview_table.setGeometry(700, size, 160, 200)
        Const.main_window.filter_preview_table.hide()
        Const.main_window.apply_filters_push_button = BasicMenuButton("Apply Filters", Const.main_window)
        size += 200
        Const.main_window.apply_filters_push_button.setGeometry(700, size, 160, 50)
        Const.main_window.apply_filters_push_button.clicked.connect(lambda: cls.apply_filter())
        Const.main_window.apply_filters_push_button.hide()

        size += 55
        Const.main_window.filters_checkbox = QCheckBox("Perform on \ncurrently displayed?", Const.main_window)
        Const.main_window.filters_checkbox.setGeometry(700, size, 160, 50)
        Const.main_window.filters_checkbox.setStyleSheet("color: rgb(255, 255, 255);")

        Const.main_window.filters_checkbox.hide()

        #
        Const.type_to_number = Const.parser.get_occurrence_from_records()
        Const.main_window.data_box.addWidget(Const.main_window.apply_filters_push_button)
        Const.main_window.data_box.addWidget(Const.main_window.filter_preview_table)
        Const.main_window.data_box.addWidget(Const.main_window.filters_checkbox)
        # find_water = Const.parser.filter_records_by_string(text_value="砂")
        Const.main_window.search_bar = QLineEdit(Const.main_window)
        Const.main_window.search_bar.setGeometry(700, 50, 150, 30)
        Const.main_window.search_bar.textChanged.connect(lambda: cls.update_by_string_search())
        Const.main_window.search_bar.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.prev_search_value = ""

        config = Const.parser.config

        if hasattr(config, "json_file"):
            Const.main_window.save_current_view_button = BasicMenuButton("Save current view", Const.main_window)
            Const.main_window.save_current_view_button.setGeometry(900, 20, 150, 60)
            Const.main_window.save_current_view_button.clicked.connect(lambda: cls.save_view())

            Const.main_window.load_view_button = BasicMenuButton("Load view", Const.main_window)
            Const.main_window.load_view_button.setGeometry(900, 90, 150, 60)
            Const.main_window.load_view_button.clicked.connect(lambda: cls.load_view())
            Const.main_window.data_box.addWidget(Const.main_window.load_view_button)

            Const.main_window.delete_view_button = BasicMenuButton("Delete view", Const.main_window)
            Const.main_window.delete_view_button.setGeometry(900, 160, 150, 60)
            Const.main_window.delete_view_button.clicked.connect(lambda: cls.delete_view())

            Const.main_window.data_box.addWidget(Const.main_window.save_current_view_button)
            Const.main_window.data_box.addWidget(Const.main_window.load_view_button)
            Const.main_window.data_box.addWidget(Const.main_window.delete_view_button)

        # view list

        Const.main_window.view_name_line_edit = QLineEdit()
        Const.main_window.view_name_line_edit.setGeometry(1070, 50, 150, 30)
        Const.main_window.view_name_line_edit.setStyleSheet("color: rgb(255, 255, 255);")

        Const.main_window.view_list = QListView()

        Const.main_window.view_list_model = QtGui.QStandardItemModel()

        Const.main_window.view_list.setModel(Const.main_window.view_list_model)

        Const.main_window.view_list.setStyleSheet("color: rgb(255, 255, 255);")

        Const.main_window.view_list.setGeometry(1070, 110, 150, 200)

        cls.refresh_views_list()

        ###/viewlist

        Const.main_window.data_box.addWidget(Const.main_window.view_name_line_edit)

        Const.main_window.data_box.addWidget(Const.main_window.view_list)

        Const.main_window.data_box.addWidget(Const.main_window.search_bar)

        Const.main_window.data_box.addWidget(Const.main_window.preview_table)

        # choose gamemode

        Const.main_window.horizontalLayout = QHBoxLayout()
        Const.main_window.horizontalLayout.setObjectName("horizontalLayout")
        Const.main_window.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        Const.main_window.horizontalLayout.setGeometry(QRect(20, 450, 751, 161))
        Const.main_window.verticalLayout_2 = QVBoxLayout()
        Const.main_window.verticalLayout_2.setObjectName("verticalLayout_2")
        Const.main_window.radioButton = QRadioButton(Const.main_window)
        Const.main_window.radioButton.setObjectName("radioButton")
        Const.main_window.radioButton.setGeometry(QRect(20, 500, 100, 50))
        Const.main_window.radioButton.setText("Falling Blocks")

        Const.main_window.radioButton.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.radioButton.setChecked(True)

        Const.main_window.verticalLayout_2.addWidget(Const.main_window.radioButton)

        Const.main_window.radioButton_2 = QRadioButton(Const.main_window)
        Const.main_window.radioButton_2 = QRadioButton(Const.main_window)
        Const.main_window.radioButton_2.setObjectName("radioButton_2")
        Const.main_window.radioButton_2.setGeometry(QRect(20, 550, 100, 50))
        Const.main_window.radioButton_2.setText("ABCD Choice")
        Const.main_window.radioButton_2.setStyleSheet("color: rgb(255, 255, 255);")

        Const.main_window.verticalLayout_2.addWidget(Const.main_window.radioButton_2)

        # Const.main_window.radioButton_3 = QRadioButton(Const.main_window)
        # Const.main_window.radioButton_3.setObjectName("radioButton_3")
        # Const.main_window.radioButton_3.setGeometry(QRect(20, 600, 100, 50))
        # Const.main_window.radioButton_3.setText("Fill the gaps")
        # Const.main_window.radioButton_3.setStyleSheet("color: rgb(255, 255, 255);")
        #
        # Const.main_window.verticalLayout_2.addWidget(Const.main_window.radioButton_3)
        #
        # Const.main_window.radioButton_4 = QRadioButton(Const.main_window)
        # Const.main_window.radioButton_4.setObjectName("radioButton_4")
        # Const.main_window.radioButton_4.setGeometry(QRect(20, 650, 100, 50))
        # Const.main_window.radioButton_4.setText("Match records")
        # Const.main_window.radioButton_4.setStyleSheet("color: rgb(255, 255, 255);")
        #
        # Const.main_window.verticalLayout_2.addWidget(Const.main_window.radioButton_4)

        Const.main_window.data_box.addLayout(Const.main_window.verticalLayout_2)

        Const.main_window.verticalLayout = QVBoxLayout()
        Const.main_window.verticalLayout.setObjectName("verticalLayout")
        Const.main_window.label_batch = QLabel(Const.main_window)
        Const.main_window.label_batch.setObjectName("label")
        Const.main_window.label_batch.setLayoutDirection(Qt.RightToLeft)
        Const.main_window.label_batch.setGeometry(QRect(150, 500, 180, 50))
        Const.main_window.label_batch.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.label_batch.setText("Choose batch size: 100 > x > 10")
        # label.setLayoutDirection(Qt::RightToLeft)

        Const.main_window.label_batch.setAlignment(Qt.AlignCenter)

        Const.main_window.verticalLayout.addWidget(Const.main_window.label_batch)

        Const.main_window.batchSize = QSpinBox(Const.main_window)
        Const.main_window.batchSize.setObjectName("batchSize")
        Const.main_window.batchSize.setGeometry(QRect(180, 560, 120, 50))
        Const.main_window.batchSize.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.batchSize.setValue(10)
        Const.main_window.batchSize.setMinimum(10)
        Const.main_window.batchSize.setMaximum(100)

        Const.main_window.verticalLayout.addWidget(Const.main_window.batchSize)

        Const.main_window.horizontalLayout.addLayout(Const.main_window.verticalLayout)

        ###
        Const.main_window.label_iteration_size = QLabel(Const.main_window)
        Const.main_window.label_iteration_size.setObjectName("label")
        Const.main_window.label_iteration_size.setLayoutDirection(Qt.RightToLeft)
        Const.main_window.label_iteration_size.setGeometry(QRect(350, 500, 200, 50))
        Const.main_window.label_iteration_size.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.label_iteration_size.setText("Choose number of record in one iter.")
        # label.setLayoutDirection(Qt::RightToLeft)

        Const.main_window.label_iteration_size.setAlignment(Qt.AlignCenter)

        Const.main_window.verticalLayout.addWidget(Const.main_window.label_iteration_size)

        Const.main_window.iteration_size = QSpinBox(Const.main_window)
        Const.main_window.iteration_size.setObjectName("batchSize")
        Const.main_window.iteration_size.setGeometry(QRect(380, 560, 120, 50))
        Const.main_window.iteration_size.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.iteration_size.setValue(4)
        Const.main_window.iteration_size.setMinimum(2)
        Const.main_window.iteration_size.setMaximum(10)

        Const.main_window.verticalLayout.addWidget(Const.main_window.iteration_size)

        ### columns

        Const.main_window.translate_from_list = QListView()
        Const.main_window.translate_to_list = QListView()

        Const.main_window.translate_from_model = QtGui.QStandardItemModel()
        Const.main_window.translate_to_model = QtGui.QStandardItemModel()

        Const.main_window.translate_from_list.setModel(Const.main_window.translate_from_model)
        Const.main_window.translate_to_list.setModel(Const.main_window.translate_to_model)

        Const.main_window.translate_from_list.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.translate_to_list.setStyleSheet("color: rgb(255, 255, 255);")

        Const.main_window.translate_from_list.setGeometry(650, 500, 150, 200)
        Const.main_window.translate_to_list.setGeometry(810, 500, 150, 200)

        Const.main_window.verticalLayout.addWidget(Const.main_window.translate_from_list)
        Const.main_window.verticalLayout.addWidget(Const.main_window.translate_to_list)

        cls.set_from_and_to_models()

        Const.main_window.horizontalLayout.addLayout(Const.main_window.verticalLayout)

        ###
        Const.main_window.pushButton = BasicMenuButton("Start Game!", Const.main_window)

        Const.main_window.pushButton.setObjectName("Start Game")

        Const.main_window.pushButton.clicked.connect(lambda: cls.start_game())

        Const.main_window.pushButton.setGeometry(QRect(1000, 500, 120, 50))

        Const.main_window.horizontalLayout.addWidget(Const.main_window.pushButton)

        # Const.main_window.main_menu_box.addLayout(Const.main_window.horizontalLayout)
        Const.main_window.data_box.addLayout(Const.main_window.horizontalLayout)

        Const.main_window.main_menu_box.addLayout(Const.main_window.data_box, 5)

        Const.main_window.mode_radios = [
            Const.main_window.radioButton_2,
            Const.main_window.radioButton]

        Const.main_window.task_attributes.extend([Const.main_window.pushButton, Const.main_window.horizontalLayout,
                                                  Const.main_window.verticalLayout, Const.main_window.batchSize,
                                                  Const.main_window.label_batch, Const.main_window.verticalLayout_2,
                                                  Const.main_window.radioButton_2, Const.main_window.radioButton,
                                                  Const.main_window.search_bar, Const.main_window.filters_checkbox,
                                                  Const.main_window.apply_filters_push_button,
                                                  Const.main_window.filter_preview_table,
                                                  Const.main_window.filter_list_widget,
                                                  Const.main_window.deselect_displayed,
                                                  Const.main_window.select_displayed,
                                                  Const.main_window.show_only_deselected,
                                                  Const.main_window.show_only_selected,
                                                  Const.main_window.show_all_button,
                                                  Const.main_window.iteration_size,
                                                  Const.main_window.label_iteration_size,

                                                  ])

    @classmethod
    def refresh_views_list(cls):
        try:
            with open(Const.parser.config.json_file, ) as json_path:
                views_names = json.load(json_path).get("saved_views", {})
        except AttributeError:

            views_names = {}

        Const.main_window.view_list_model.removeRows(0, Const.main_window.view_list_model.rowCount())

        for key, value in views_names.items():
            size = len(value.get('selected_records', []))
            text_value = f"{key} ({size})"

            item = QtGui.QStandardItem(text_value)
            item.real_name = key

            Const.main_window.view_list_model.appendRow(item)

        Const.main_window.view_list.setModel(Const.main_window.view_list_model)

    @classmethod
    def set_from_and_to_models(cls):

        columns = Const.parser.config.words + Const.parser.config.sentences
        if len(columns) == 0:
            columns = Const.parser.headers_to_numbers.keys()
        for column in columns:
            item = QtGui.QStandardItem(column)
            item.real_name = column
            item_1 = QtGui.QStandardItem(column)
            item_1.real_name = column

            Const.main_window.translate_from_model.appendRow(item)
            Const.main_window.translate_to_model.appendRow(item_1)

        Const.main_window.translate_from_list.setModel(Const.main_window.translate_from_model)
        Const.main_window.translate_to_list.setModel(Const.main_window.translate_to_model)

    @classmethod
    def fill_filter_preview_table(cls):
        selected_value = Const.main_window.filter_list_widget.currentItem().text()
        if selected_value == "NONE":
            Const.main_window.filter_preview_table.hide()
            Const.main_window.apply_filters_push_button.hide()
            Const.main_window.filters_checkbox.hide()
        else:
            Const.main_window.filter_preview_table.show()
            Const.main_window.apply_filters_push_button.show()
            Const.main_window.filters_checkbox.show()
            Const.main_window.filter_preview_table.clearContents()
            Const.main_window.filter_preview_table.setColumnCount(1)
            Const.main_window.filter_preview_table.setHorizontalHeaderLabels([selected_value])
            values = Const.type_to_number[Const.parser.remove_wrong_letters(selected_value)]
            Const.main_window.filter_preview_table.setRowCount(len(values.keys()) + 1)
            i = 0
            for key, value in values.items():
                text_to_add = f"{key} {UFTIcons.RIGHT_ARROW} {value}"
                # Const.main_window.filter_preview_table.insertRow(0)

                tableItem = QTableWidgetItem(str(text_to_add))
                tableItem.setForeground(QBrush(QColor(255, 255, 255)))
                tableItem.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)

                tableItem.setCheckState(Qt.CheckState.Checked)

                # tableItem.clicked.connect(lambda: cls.append_to_currently_used(record.ID, tableItem))
                Const.main_window.filter_preview_table.setItem(i, 0, tableItem)
                i += 1

    @classmethod
    def apply_filter(cls):
        playsound("sounds/regular_click.wav")
        key = Const.main_window.filter_list_widget.currentItem().text()
        key = Const.parser.remove_wrong_letters(key)
        filter_only = []
        for i in range(Const.main_window.filter_preview_table.rowCount()):
            item = Const.main_window.filter_preview_table.item(i, 0)
            if item:
                if item.checkState() == Qt.CheckState.Checked:
                    filter_only.append(item.text())

        filter_only = [values.split(f" {UFTIcons.RIGHT_ARROW}")[0]
                       for values in filter_only]

        search_vector = {key: filter_only}
        if Const.main_window.filters_checkbox.isChecked():
            search_vector["tab"] = Const.main_window.currently_used_records

        Const.main_window.currently_used_records = Const.parser.filter_records(**search_vector)

        cls.fill_preview_table_with_current_state()

    @classmethod
    def update_by_string_search(cls):
        text_value = Const.main_window.search_bar.text()

        if text_value != Const.main_window.prev_search_value:
            Const.main_window.currently_used_records = Const.parser.filter_records_by_string(text_value=text_value)
            cls.fill_preview_table_with_current_state()
            Const.main_window.prev_search_value = text_value

    @classmethod
    def show_only_selected(cls, selected: bool, perform_sync=True):
        playsound("sounds/regular_click.wav")
        if perform_sync:
            cls.synchronise_checked()
        if selected:
            Const.main_window.currently_used_records = [record for record in Const.parser.all_records
                                                        if record.ID in Const.main_window.all_selected_records]
        else:
            Const.main_window.currently_used_records = [record for record in Const.parser.all_records
                                                        if record.ID not in Const.main_window.all_selected_records]
        cls.fill_preview_table_with_current_state()

    @classmethod
    def show_me_all(cls):
        playsound("sounds/regular_click.wav")
        Const.main_window.currently_used_records = Const.parser.all_records
        cls.fill_preview_table_with_current_state()

    @classmethod
    def select_all_in_current_view(cls, deselect=False):
        playsound("sounds/regular_click.wav")
        if deselect:
            check_state = Qt.CheckState.Unchecked
        else:
            check_state = Qt.CheckState.Checked
        for i in range(Const.main_window.preview_table.rowCount()):
            item = Const.main_window.preview_table.item(i, 0)
            if item:
                item.setCheckState(check_state)
                if deselect:
                    try:
                        Const.main_window.all_selected_records.remove(int(item.text()))
                    except ValueError:
                        pass
                else:
                    Const.main_window.all_selected_records.append(int(item.text()))
        Const.main_window.all_selected_records = list(set(Const.main_window.all_selected_records))

    @classmethod
    def synchronise_checked(cls):
        for i in range(Const.main_window.preview_table.rowCount()):
            item = Const.main_window.preview_table.item(i, 0)
            if item:
                if item.checkState() == Qt.CheckState.Checked:
                    Const.main_window.all_selected_records.append(int(item.text()))
                elif item.checkState() == Qt.CheckState.Unchecked:
                    try:
                        Const.main_window.all_selected_records.remove(int(item.text()))
                    except ValueError:
                        pass
        Const.main_window.all_selected_records = list(set(Const.main_window.all_selected_records))

    @classmethod
    def fill_preview_table_with_current_state(cls, perform_sync=True):
        if perform_sync:
            cls.synchronise_checked()
        Const.main_window.preview_table.clearContents()
        size = len(Const.main_window.currently_used_records) + 1
        Const.main_window.preview_table.setRowCount(size)

        Const.main_window.preview_table.setColumnCount(len(Const.parser.headers) + 1)

        headers = [header[0] for header in Const.parser.headers]
        Const.main_window.preview_table.setHorizontalHeaderLabels(["ID", *headers])

        for record in reversed(Const.main_window.currently_used_records):
            values = list(asdict(record).values())
            Const.main_window.preview_table.insertRow(0)
            tableItem = QTableWidgetItem(str(record.ID))
            tableItem.setForeground(QBrush(QColor(255, 255, 255)))
            tableItem.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            if record.ID in Const.main_window.all_selected_records:
                tableItem.setCheckState(Qt.CheckState.Checked)
            else:
                tableItem.setCheckState(Qt.CheckState.Unchecked)
            # tableItem.clicked.connect(lambda: cls.append_to_currently_used(record.ID, tableItem))
            Const.main_window.preview_table.setItem(0, 0, tableItem)
            for col_index, value in enumerate(values):
                if isinstance(value, (float, int)):
                    value = '{0:0,.0f}'.format(value)
                tableItem = QTableWidgetItem(str(value))
                tableItem.setForeground(QBrush(QColor(255, 255, 255)))
                Const.main_window.preview_table.setItem(0, col_index + 1, tableItem)
        for i in range(size, 2 * size):
            Const.main_window.preview_table.removeRow(size)

    @classmethod
    def collect_game_data(cls):
        Const.iter_size = int(Const.main_window.iteration_size.text())

        Const.batch_size = int(Const.main_window.batchSize.text())

        if Const.iter_size > Const.batch_size:
            return False, "itersize cant be bigger than batch size"
        if Const.batch_size > len(Const.main_window.all_selected_records):
            return False, f"you need at least {Const.batch_size} records selected."
        return True, ""

    @classmethod
    def collect_current_view(cls):
        return {"iter_size": int(Const.main_window.iteration_size.text()),
                "batch_size": int(Const.main_window.batchSize.text()),
                "selected_records": Const.main_window.all_selected_records,
                "game_mode": [radio.text() for radio in Const.main_window.mode_radios if radio.isChecked()][0]}

    @classmethod
    def save_view(cls):
        cls.synchronise_checked()
        view_name = Const.main_window.view_name_line_edit.text()
        config = Const.parser.config
        """                with open(path, ) as json_file:
                    configurations = json.load(json_file)"""
        with open(config.json_file, ) as json_path:
            json_file = json.load(json_path)
            if not json_file.get("saved_views"):
                json_file["saved_views"] = {}
            json_file["saved_views"][view_name] = cls.collect_current_view()
            config.saved_views = json_file["saved_views"]
            new_json_file = json_file
        try:
            with open(config.json_file, "w") as out_file:
                json.dump(new_json_file, out_file, indent=4)
        except FileNotFoundError:
            display_error_window("No proper file location")
            return False
        cls.refresh_views_list()

    @classmethod
    def get_selected_view(cls):

        selected = Const.main_window.view_list.currentIndex().row()

        return Const.main_window.view_list_model.item(selected, 0).real_name

    @classmethod
    def delete_view(cls):
        view_name = cls.get_selected_view()

        config = Const.parser.config
        """                with open(path, ) as json_file:
                    configurations = json.load(json_file)"""
        with open(config.json_file, ) as json_path:
            json_file = json.load(json_path)
            if not json_file.get("saved_views"):
                json_file["saved_views"] = {}

            reduced_views = {k: v for k, v in json_file["saved_views"].items() if k != view_name}
            json_file["saved_views"] = reduced_views
            new_json_file = json_file
        try:
            with open(config.json_file, "w") as out_file:
                json.dump(new_json_file, out_file, indent=4)
        except FileNotFoundError:

            display_error_window("No proper file location")
            return False
        cls.refresh_views_list()

    @classmethod
    def load_view(cls):
        view_name = cls.get_selected_view()
        cls.show_me_all()
        cls.select_all_in_current_view(deselect=True)

        config = Const.parser.config
        if view_to_apply := config.saved_views.get(view_name):
            # cls.show_me_all()
            # Const.main_window.currently_used_records = Const.parser.all_records
            Const.main_window.all_selected_records = list(set(view_to_apply.get("selected_records", [])))

            # cls.show_me_all()
            is_set = False
            if chosen_radio := view_to_apply.get("game_mode"):
                for radio in Const.main_window.mode_radios:
                    if radio.text() == chosen_radio:
                        radio.setChecked(True)
                        is_set = True
                    else:
                        radio.setChecked(False)
            if not is_set:
                Const.main_window.mode_radios[0].setChecked(True)

            Const.main_window.iteration_size.setValue(view_to_apply.get("iter_size", 4))
            Const.main_window.batchSize.setValue(view_to_apply.get("batch_size", 10))

            cls.show_only_selected(selected=True, perform_sync=False)
            cls.select_all_in_current_view()

            Const.main_window.view_name_line_edit.setText(view_name)

        else:
            return

    @classmethod
    def get_translate_from_to(cls):
        selected = Const.main_window.translate_from_list.currentIndex().row()
        selected_1 = Const.main_window.translate_to_list.currentIndex().row()

        return Const.main_window.translate_from_model.item(selected,
                                                           0).real_name, Const.main_window.translate_to_model.item(
            selected_1, 0).real_name

    @classmethod
    def start_game(cls):
        cls.synchronise_checked()
        status, msg = cls.collect_game_data()
        _from, _to = cls.get_translate_from_to()
        if status:
            for radio in Const.main_window.mode_radios:
                if radio.isChecked():
                    Const.main_window.start_game(mode=radio.text(), _from=_from, _to=_to)
        else:
            playsound("sounds/failure.mp3", False)
            display_error_window(msg)
