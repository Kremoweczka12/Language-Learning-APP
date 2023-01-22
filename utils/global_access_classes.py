import itertools

from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QSizePolicy, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QWidget, \
    QScrollArea
from playsound import playsound

from utils.CONSTANTS import StyleSheets, StagesOrdering


class CurrentlyEdited:
    config_in_progress = None


class Const:
    GRAND_ITER = itertools.count()
    main_window = None
    parser = None
    type_to_number = None
    batch_size = 10
    iter_size = 2
    current_batch = 1
    temp_sound_path_sentence = ""
    temp_sound_path_word = ""


class Config:
    def __init__(self, words=None, words_sounds=None, images=None, sentences=None,
                 sentences_sounds=None, filters_columns=None, absolute_path_to_file="", words_sounds_path="",
                 sentences_sounds_path="", images_path="", saved_views=None):
        if saved_views is None:
            saved_views = {}
        self.interesting_columns = []
        self.absolute_path_to_file = absolute_path_to_file
        if filters_columns is None:
            filters_columns = []
        if sentences_sounds is None:
            sentences_sounds = ""

        if sentences is None:
            sentences = []
        if words_sounds is None:
            words_sounds = ""
        if images is None:
            images = ""
        if words is None:
            words = []
        self.images = images

        self.sentences = sentences
        self.words = words
        self.words_sounds = words_sounds
        self.sentences_sounds = sentences_sounds
        self.filters_columns = filters_columns
        self.words_sounds_path = words_sounds_path
        self.sentences_sounds_path = sentences_sounds_path
        self.images_path = images_path
        self.saved_views = saved_views
        self.get_interesting_headers()

    def get_interesting_headers(self):
        for element in StagesOrdering.CONFIG_CREATION_STAGES:
            attribute = getattr(self, element)
            if isinstance(attribute, list):
                self.interesting_columns.extend(attribute)
            elif isinstance(attribute, str):
                self.interesting_columns.append(attribute)
        self.interesting_columns = list(set(self.interesting_columns))


class BasicMenuButton(QPushButton):
    def __init__(self, text: str, parent):
        super().__init__(text, parent)

        self.setStyleSheet(StyleSheets.TASK_BAR_BUTTON_SHEET)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class ErrorDialog(QDialog):
    def __init__(self, msg):
        super().__init__()

        self.setWindowTitle("Error")

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        self.layout = QVBoxLayout()
        message = QLabel(msg)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


def play_safe_sound(is_sentence=False):
    path = "no path"
    try:
        if is_sentence:
            path = Const.temp_sound_path_sentence

        else:
            path = Const.temp_sound_path_word
        playsound(path, False)
    except Exception as e:
        playsound("sounds/failure.mp3", False)

        error_msg = f"are you sure {path} is a proper path to proper file?"
        if not path:
            error_msg = "There is no sound folder connected to your config"
        dlg = ErrorDialog(error_msg)
        dlg.setWindowTitle("ERROR")
        dlg.exec_()


class ScrollLabel(QScrollArea):

    # constructor
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        # making widget resizable
        self.setWidgetResizable(True)

        # making qwidget object
        content = QWidget(self)
        self.setWidget(content)

        # vertical box layout
        self.lay = QVBoxLayout(content)

        # creating label
        self.label = QLabel(content)

        # setting alignment to the text
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label.setWordWrap(True)

        self.play_word_sound_button = QPushButton("Word writings:")

        self.play_word_sound_button.setStyleSheet(StyleSheets.PLAY_WORD_SOUND_BUTTON)
        self.play_word_sound_button.clicked.connect(lambda: play_safe_sound())
        self.play_word_sound_button.setIcon(QtGui.QPixmap('icon/headphones.png'))
        self.lay.addWidget(self.play_word_sound_button)

        # adding label to the layout
        self.lay.addWidget(self.label)
        self.lay.setSpacing(0)

        self.play_sentence_sound_button = QPushButton("Sample usages:")
        self.play_sentence_sound_button.setStyleSheet(StyleSheets.PLAY_WORD_SOUND_BUTTON)
        self.play_sentence_sound_button.clicked.connect(lambda: play_safe_sound(is_sentence=True))
        self.play_sentence_sound_button.setIcon(QtGui.QPixmap('icon/headphones.png'))
        self.lay.addWidget(self.play_sentence_sound_button)

        # creating label
        self.label_1 = QLabel(content)

        # setting alignment to the text
        self.label_1.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # making label multi-line
        self.label_1.setWordWrap(True)

        self.lay.addWidget(self.label_1)

    # the setText method
    def setText(self, text, text_1):
        # setting text to the label
        self.label.setText(text)
        self.label_1.setText(text_1)
