from PySide6 import QtGui
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QGridLayout, QVBoxLayout
from utils.global_access_classes import Const, BasicMenuButton, ScrollLabel
from windows.windows_handlers.creation_handler import FirstViewWindowHandler
from windows.windows_handlers.excercise_handler import FallingWindowsHandler, ABCDWindowsHandler


class MainWindow(QMainWindow):
    modes = {"Falling Blocks": FallingWindowsHandler, "ABCD Choice": ABCDWindowsHandler}

    def kill_exercise_task(self):
        for attribute in self.task_attributes:
            attribute.deleteLater()

    def start_game(self, mode, _from, _to):


        handler_mode = self.modes.get(mode, ABCDWindowsHandler)
        handler_mode.kill_exercise_task()
        self.restart_button = BasicMenuButton("Restart", self)
        self.restart_button.clicked.connect(lambda: handler_mode.restart_batch(is_full_restart=True))

        self.kill_button = BasicMenuButton("Kill Process", self)
        self.kill_button.clicked.connect(lambda: handler_mode.reload_data_display_mode())

        self.left_height_box = QGridLayout(self)

        self.left_height_box.addWidget(self.restart_button, 2, 0, )
        self.left_height_box.addWidget(self.kill_button, 3, 0, )
        self.left_height_box.setSpacing(0)

        self.right_side_features = QGridLayout(self)

        self.right_side_boxes = QHBoxLayout(self)
        self.right_side_infos = QVBoxLayout(self)

        # self.word_info = QLabel("ITS SAMPLE WORD")
        self.word_info = ScrollLabel()
        self.word_info.setText("NONE IS WRITTEN", "NONE AS WELL")
        self.word_info.setStyleSheet("color: rgb(255, 255, 255); font-size: 16pt;")

        policy = self.word_info.sizePolicy()
        self.next_word_button = BasicMenuButton("Next Word", self)
        self.next_word_button.setMaximumHeight(int(self.height() / 7))
        self.hint_button = BasicMenuButton("Give me a hint", self)
        self.hint_button.setMaximumHeight(int(self.height() / 7))
        self.display_details = BasicMenuButton("Display details.", self)
        self.display_details.setMaximumHeight(int(self.height() / 7))
        self.right_side_infos.addWidget(self.word_info)
        self.right_side_infos.addWidget(self.next_word_button)
        self.right_side_infos.addWidget(self.hint_button)
        self.right_side_infos.addWidget(self.display_details)
        self.right_side_features.addLayout(self.right_side_boxes, 0, 0, 3, 1)
        self.right_side_features.addLayout(self.right_side_infos, 4, 0)

        self.word_info.hide()
        self.display_details.hide()
        self.next_word_button.hide()
        # self.hint_button.hide()

        # self.hint_button.hide()
        self.hint_button.setSizePolicy(policy)
        self.display_details.setSizePolicy(policy)
        self.next_word_button.setSizePolicy(policy)

        self.all_boxes = QHBoxLayout(self)
        self.all_boxes.addLayout(self.left_height_box, 1)
        self.all_boxes.addLayout(self.right_side_features, 4)
        # add mapping to proper handling
        # FallingWindowsHandler.initiate_task()
        handler_mode.initiate_task(_from, _to)
        self.setCentralWidget(QWidget(self))

        self.centralWidget().setLayout(self.all_boxes)
        self.task_attributes.extend([self.all_boxes])

    def __init__(self):
        super().__init__()
        Const.main_window = self
        self.setWindowTitle("PRO Lingua")
        self.setFixedSize(QSize(1280, 720))
        self.setWindowIcon(QtGui.QIcon("icons/brain.png"))

        # self.start_game("falling blocks")

        FirstViewWindowHandler.initiate_task()

        self.setStyleSheet("background-color: #2D2D2D;")
        self.show()
