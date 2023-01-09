import random
import time
from dataclasses import asdict
from math import ceil

import playsound
from PySide6.QtCore import QPropertyAnimation, QPoint, Qt
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QScrollArea, QGroupBox, QFormLayout, QVBoxLayout

from utils.CONSTANTS import StyleSheets
from utils.global_access_classes import Const, LeftMenuButton, play_safe_sound
from windows.windows_handlers.base_handler import BaseHandler
from windows.windows_handlers.creation_handler import FirstViewWindowHandler
from windows.windows_handlers.data_loading_handler import LoadedDataWindowHandler


class ExerciseBaseHandler(BaseHandler):
    anims = []
    buttons = []
    game_record = []
    failed_words = []
    compare_from = "vocab_kana"
    compare_to = "vocab_meaning"
    labels_list = []
    buttons_list = []
    is_at_summary = False
    is_game_won = False

    @classmethod
    def reload_data_display_mode(cls):
        cls.labels_list = []
        cls.buttons_list = []
        cls.buttons = []
        cls.game_record = []
        cls.failed_words = []

        super().kill_exercise_task(spare_loading_parts=True)
        FirstViewWindowHandler.initiate_task()
        # super().kill_exercise_task(spare_loading_parts=False)
        # FirstViewWindowHandler.reload_config_or_raw_data(is_raw=False)

    @classmethod
    def display_info_in_label(cls, text):
        Const.main_window.word_info.show()
        Const.main_window.word_info.setText(text)

    @classmethod
    def display_info_in_label_from_record(cls, record):
        parser = Const.parser
        config = parser.config
        record_dict = cls.update_sound_consts(record)

        words = ''.join([f" - {record_dict[Const.parser.remove_wrong_letters(word.lower())]}\n"
                         for word in config.words])
        sentences = ''.join([f"- {record_dict[Const.parser.remove_wrong_letters(sentence.lower())]}\n"
                             for sentence in config.sentences])
        sentences = Const.parser.put_space_bars(sentences)
        words = Const.parser.put_space_bars(words)
        word_label_text = f"{words}\nSample usages:{sentences}"
        Const.main_window.word_info.show()
        Const.main_window.word_info.setText(words, sentences)

    @classmethod
    def update_sound_consts(cls, record):
        record_dict = asdict(record)

        parser = Const.parser
        config = parser.config
        word_sound_file_name = record_dict[parser.remove_wrong_letters(config.words_sounds.lower())]
        if word_sound_file_name.startswith("[sound:"):
            word_sound_file_name = word_sound_file_name[7:-1]

        Const.temp_sound_path_word = f"{config.words_sounds_path}/{word_sound_file_name}"

        sentence_sound_file_name = record_dict[parser.remove_wrong_letters(config.sentences_sounds.lower())]
        if sentence_sound_file_name.startswith("[sound:"):
            sentence_sound_file_name = sentence_sound_file_name[7:-1]

        Const.temp_sound_path_sentence = f"{config.sentences_sounds_path}/{sentence_sound_file_name}"
        return record_dict

    @classmethod
    def create_batch_summary(cls):
        cls.is_at_summary = True
        for anim in cls.anims:
            anim.stop()
        Const.main_window.hint_button.hide()
        Const.main_window.form_layout = QFormLayout()
        Const.main_window.group_box = QGroupBox("This box contains incorrectly matched")

        for button in cls.buttons:
            button.hide()

        failed_records = [record for record in cls.game_record if record.ID in cls.failed_words]

        for i, record in enumerate(failed_records):
            record_dict = asdict(record)
            label_text = f"'{record_dict[cls.compare_from]}' matches with: '{record_dict[cls.compare_to]}'"
            cls.labels_list.append(QLabel(label_text))
            button = LeftMenuButton("More...", Const.main_window)
            button.clicked.connect(lambda checked=False, device=record: cls.display_info_in_label_from_record(device))
            button.setMaximumHeight(int(Const.main_window.height() / 10))
            cls.buttons_list.append(button)
            print(i)
            Const.main_window.form_layout.addRow(cls.labels_list[i], cls.buttons_list[i])

        for label in cls.labels_list:
            label.setStyleSheet("color: rgb(255, 255, 255);")

        Const.main_window.group_box.setLayout(Const.main_window.form_layout)
        Const.main_window.scroll = QScrollArea()
        Const.main_window.scroll.setWidget(Const.main_window.group_box)
        Const.main_window.scroll.setWidgetResizable(True)
        Const.main_window.scroll.setFixedHeight(400)

        Const.main_window.errors_layout = QVBoxLayout()
        Const.main_window.errors_layout.addWidget(Const.main_window.scroll)

        Const.main_window.next_batch_button = QPushButton("Next Batch")
        Const.main_window.next_batch_button.setStyleSheet("color: #ffffff;")
        Const.main_window.errors_layout.addWidget(Const.main_window.next_batch_button)

        Const.main_window.restart_batch_button = QPushButton("Restart Batch")
        Const.main_window.restart_batch_button.setStyleSheet("color: #ffffff;")

        Const.main_window.errors_layout.addWidget(Const.main_window.restart_batch_button)

        Const.main_window.right_side_features.addLayout(Const.main_window.errors_layout, 5, 0)

    @classmethod
    def destroy_summary_buttons(cls):
        Const.main_window.word_info.hide()
        try:
            try:
                Const.main_window.group_box.deleteLater()
                Const.main_window.scroll.deleteLater()
                Const.main_window.errors_layout.deleteLater()
            except Exception as e:
                print(e)
            for button in cls.buttons_list:
                button.deleteLater()
            for label in cls.labels_list:
                label.deleteLater()

            cls.labels_list = []
            cls.buttons_list = []

            Const.main_window.next_batch_button.deleteLater()
            Const.main_window.restart_batch_button.deleteLater()
            Const.main_window.hint_button.show()
            for anim in cls.anims:
                anim.stop()
                anim.start()

        except Exception as e:
            print(e)
            return

    @classmethod
    def restart_batch(cls, is_full_restart=False):
        Const.main_window.word_info.hide()
        cls.is_at_summary = False
        playsound.playsound("sounds/regular_click.wav", False)
        cls.failed_words = []
        Const.current_batch -= 1
        if is_full_restart:
            Const.current_batch = 1

        cls.unused = cls.game_record[
                     (Const.current_batch - 1) * Const.batch_size:Const.current_batch * Const.batch_size]

        cls.already_used = []
        cls.destroy_summary_buttons()

        for button in cls.buttons:
            button.show()
        for anim in cls.anims:
            anim.stop()
            anim.start()


class FallingWindowsHandler(ExerciseBaseHandler):
    current_batch = []
    current_iter = []
    anims = []
    buttons = []
    game_record = []
    compare_from = "vocab_kana"
    compare_to = "vocab_meaning"
    currently_correct = ""
    already_used = []
    unused = []
    used_ids = []
    number_of_batches = 0
    is_game_won = False
    is_at_summary = False
    failed_words = []

    @classmethod
    def restart_batch(cls, is_full_restart=False):
        super().restart_batch(is_full_restart)
        Const.main_window.hint_button.hide()
        cls.select_records_for_iter()
        current_batch_and_iter_text = f"batch: {Const.current_batch}/{cls.number_of_batches} \n" \
                                      f" iter: {len(cls.already_used)}/{len(cls.unused) + len(cls.already_used)}"
        Const.main_window.batch_and_iter.setText(current_batch_and_iter_text)

    @classmethod
    def restart_animations(cls):
        for anim in cls.anims:
            anim.stop()
        for anim in cls.anims:
            anim.start()

    @classmethod
    def win_action(cls):
        for anim in cls.anims:
            anim.stop()
        for button in cls.buttons:
            button.hide()

        for button in cls.buttons:
            button.hide()

        # Const.main_window.you_won_label = QLabel(Const.main_window)
        # Const.main_window.you_won_label.setText("You have won!")
        # Const.main_window.you_won_label.setAlignment(Qt.AlignCenter)
        # Const.main_window.you_won_label.setStyleSheet("color: rgb(255, 255, 255);")
        # Const.main_window.right_side_boxes.addWidget(Const.main_window.you_won_label)
        # Const.main_window.task_attributes.append(Const.main_window.you_won_label)

        cls.is_game_won = True
        Const.main_window.next_batch_button.hide()

    @classmethod
    def pick_answer_action(cls, button):
        if asdict(cls.currently_correct)[cls.compare_from] == button.text():
            playsound.playsound("sounds/correct.wav", False)
            print("correct!!")
            cls.select_records_for_iter()
            cls.restart_animations()
        else:
            playsound.playsound("sounds/failure.mp3", False)
            cls.failed_words.append(cls.currently_correct.ID)
            cls.failed_words = list(set(cls.failed_words))
            print(cls.failed_words)
            print("FALSE")
            cls.select_records_for_iter()
            cls.restart_animations()

    @classmethod
    def force_bad_answer(cls):
        if not cls.is_at_summary:
            playsound.playsound("sounds/failure.mp3", False)
            cls.failed_words.append(cls.currently_correct.ID)
            cls.failed_words = list(set(cls.failed_words))
            print(cls.failed_words)
            print("FALSE")
            cls.select_records_for_iter()
            cls.restart_animations()

    @classmethod
    def create_buttons(cls):
        buttons = []
        anims = []
        start_point = 270
        increment_by = int(1000 / Const.iter_size)
        for i in range(Const.iter_size):
            button = QPushButton("Press Me!", Const.main_window)
            button.setStyleSheet(StyleSheets.FALLING_BUTTON_STYLE_SHEET)
            button.clicked.connect(lambda checked=False, device=button: cls.pick_answer_action(device))
            # button.clicked.connect(lambda: cls.pick_answer_action(button))
            Const.main_window.right_side_boxes.addWidget(button)
            anim = QPropertyAnimation(button, b"pos")
            anim.setStartValue(QPoint(start_point, 50))
            anim.setEndValue(QPoint(start_point, 650))
            anim.setDuration(2500 * Const.iter_size)
            start_point += increment_by
            anim.finished.connect(lambda: cls.force_bad_answer())
            buttons.append(button)
            anims.append(anim)

        # Const.main_window.task_attributes = [*buttons,
        #                                      *anims]
        cls.buttons = buttons
        cls.anims = anims
        cls.select_records_for_iter()
        for anim in anims:
            anim.start()

    @classmethod
    def select_records_for_iter(cls):
        cls.is_at_summary = False

        cls.destroy_summary_buttons()
        for button in cls.buttons:
            button.show()
        Const.main_window.next_word_button.hide()
        Const.main_window.display_details.hide()
        Const.main_window.word_info.hide()
        for button in cls.buttons:
            button.setStyleSheet(StyleSheets.FALLING_BUTTON_STYLE_SHEET)
        for anim in cls.anims:
            anim.stop()
        if len(cls.unused) == 0:
            print("end of batch")

            Const.current_batch += 1

            cls.unused = cls.game_record[
                         (Const.current_batch - 1) * Const.batch_size:Const.current_batch * Const.batch_size]

            cls.already_used = []
            cls.create_batch_summary()
            Const.main_window.next_batch_button.clicked.connect(lambda: cls.select_records_for_iter())
            Const.main_window.restart_batch_button.clicked.connect(lambda: cls.restart_batch())

            if len(cls.unused) == 0:
                cls.win_action()
            return

        cls.currently_correct = random.choice(cls.unused)
        cls.current_batch = cls.game_record[
                            (Const.current_batch - 1) * Const.batch_size:Const.current_batch * Const.batch_size]

        temp = cls.current_batch.copy()
        temp.remove(cls.currently_correct)
        if len(temp) < Const.iter_size - 1:
            cls.current_batch = cls.game_record[
                                (
                                        Const.current_batch - 1) * Const.batch_size - Const.iter_size:Const.current_batch * Const.batch_size]

            temp = cls.current_batch.copy()
            temp.remove(cls.currently_correct)

        cls.current_iter = random.choices(temp, k=Const.iter_size - 1)

        cls.unused.remove(cls.currently_correct)
        cls.already_used.append(cls.currently_correct)

        chosen_records = [*cls.current_iter, cls.currently_correct]
        random.shuffle(chosen_records)
        for button, iter_choice in zip(cls.buttons, chosen_records):
            button.ID = iter_choice.ID
            button.setText(asdict(iter_choice)[cls.compare_from])

        correct_answer_label_text = f"Pick up:\n {asdict(cls.currently_correct)[cls.compare_to]}"
        Const.main_window.answer_to_pick.setText(correct_answer_label_text)
        current_batch_and_iter_text = f"batch: {Const.current_batch}/{cls.number_of_batches} \n" \
                                      f" iter: {len(cls.already_used)}/{len(cls.unused) + len(cls.already_used)}"
        Const.main_window.batch_and_iter.setText(current_batch_and_iter_text)
        Const.main_window.hint_button.hide()
        for anim in cls.anims:
            anim.start()

    @classmethod
    def initiate_task(cls):
        Const.main_window.hint_button.hide()
        if hasattr(Const.main_window, "task_attributes") and Const.main_window.task_attributes is not []:
            try:
                cls.kill_exercise_task()
            except RuntimeError:
                Const.main_window.task_attributes = []
                print("already Deleted")
        Const.current_batch = 1
        cls.game_record = [record for record in Const.parser.all_records
                           if record.ID in Const.main_window.all_selected_records]
        cls.current_batch = cls.game_record[0:Const.current_batch * Const.batch_size]
        cls.unused = cls.current_batch

        Const.main_window.answer_to_pick = QLabel(Const.main_window)
        Const.main_window.answer_to_pick.setText("None")
        Const.main_window.answer_to_pick.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.answer_to_pick.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        Const.main_window.answer_to_pick.setAlignment(Qt.AlignCenter)
        Const.main_window.left_height_box.addWidget(Const.main_window.answer_to_pick, 0, 0, )
        Const.main_window.batch_and_iter = QLabel(Const.main_window)
        Const.main_window.batch_and_iter.setText("None")
        Const.main_window.batch_and_iter.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.batch_and_iter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        Const.main_window.batch_and_iter.setAlignment(Qt.AlignCenter)
        Const.main_window.left_height_box.addWidget(Const.main_window.batch_and_iter, 1, 0, )

        cls.number_of_batches = ceil(len(cls.game_record) / Const.batch_size)
        print(cls.number_of_batches)
        cls.create_buttons()

        print("intiation finished")


class ABCDWindowsHandler(ExerciseBaseHandler):
    current_batch = []
    current_iter = []

    buttons = []
    game_record = []
    compare_from = "vocab_kana"
    compare_to = "vocab_meaning"
    currently_correct = ""
    already_used = []
    unused = []
    used_ids = []
    number_of_batches = 0
    is_game_won = False
    failed_words = []

    @classmethod
    def restart_batch(cls, is_full_restart=False):
        super().restart_batch(is_full_restart)
        cls.select_records_for_iter()
        current_batch_and_iter_text = f"batch: {Const.current_batch}/{cls.number_of_batches} \n" \
                                      f" iter: {len(cls.already_used)}/{len(cls.unused) + len(cls.already_used)}"
        Const.main_window.batch_and_iter.setText(current_batch_and_iter_text)

    @classmethod
    def display_a_hint(cls):
        record = cls.currently_correct
        record_dict = asdict(record)

        parser = Const.parser
        config = parser.config
        word_sound_file_name = record_dict[parser.remove_wrong_letters(config.words_sounds.lower())]
        if word_sound_file_name.startswith("[sound:"):
            word_sound_file_name = word_sound_file_name[7:-1]

        Const.temp_sound_path_word = f"{config.words_sounds_path}/{word_sound_file_name}"

        sentence_sound_file_name = record_dict[parser.remove_wrong_letters(config.sentences_sounds.lower())]
        if sentence_sound_file_name.startswith("[sound:"):
            sentence_sound_file_name = sentence_sound_file_name[7:-1]

        Const.temp_sound_path_sentence = f"{config.sentences_sounds_path}/{sentence_sound_file_name}"

        words = ''.join([f"\n - {record_dict[Const.parser.remove_wrong_letters(word.lower())]}"
                         for word in config.words])
        sentences = ''.join([f"\n - {record_dict[Const.parser.remove_wrong_letters(sentence.lower())]}"
                             for sentence in config.sentences])
        sentences = Const.parser.put_space_bars(sentences)[1:]
        words = Const.parser.put_space_bars(words)[1:]
        word_label_text = f"{words}\nSample usages:{sentences}"
        Const.main_window.word_info.show()
        Const.main_window.word_info.setText(words, sentences)

    @classmethod
    def colour_buttons(cls):
        for _button in cls.buttons:
            if asdict(cls.currently_correct)[cls.compare_from] == _button.text():
                _button.setStyleSheet(StyleSheets.CORRECT_BUTTON_STYLE_SHEET)

    @classmethod
    def win_action(cls):

        for button in cls.buttons:
            button.hide()

        # Const.main_window.you_won_label = QLabel(Const.main_window)
        # Const.main_window.you_won_label.setText("You have won!")
        # Const.main_window.you_won_label.setAlignment(Qt.AlignCenter)
        # Const.main_window.you_won_label.setStyleSheet("color: rgb(255, 255, 255);")
        # Const.main_window.right_side_boxes.addWidget(Const.main_window.you_won_label)
        # Const.main_window.task_attributes.append(Const.main_window.you_won_label)

        cls.is_game_won = True
        Const.main_window.next_batch_button.hide()

    @classmethod
    def pick_answer_action(cls, button):
        if asdict(cls.currently_correct)[cls.compare_from] == button.text():

            print("correct!!")


            playsound.playsound("sounds/correct.wav", False)
            # cls.select_records_for_iter()
            cls.colour_buttons()
            play_safe_sound()

        else:
            playsound.playsound("sounds/failure.mp3", False)
            button.setStyleSheet(StyleSheets.FALSE_BUTTON_STYLE_SHEET)
            cls.colour_buttons()
            cls.failed_words.append(cls.currently_correct.ID)
            cls.failed_words = list(set(cls.failed_words))
            print(cls.failed_words)
            print("FALSE")
            # cls.select_records_for_iter()

        Const.main_window.next_word_button.show()
        Const.main_window.display_details.show()

    @classmethod
    def create_buttons(cls):
        buttons = []
        anims = []
        start_point = 270
        increment_by = int(1000 / Const.iter_size)
        for i in range(Const.iter_size):
            button = QPushButton("Press Me!", Const.main_window)
            button.setStyleSheet(StyleSheets.FALLING_BUTTON_STYLE_SHEET)
            button.clicked.connect(lambda checked=False, device=button: cls.pick_answer_action(device))
            # button.clicked.connect(lambda: cls.pick_answer_action(button))
            Const.main_window.right_side_boxes.addWidget(button)

            start_point += increment_by

            buttons.append(button)

        # Const.main_window.task_attributes = [*buttons,
        #                                      *anims]
        cls.buttons = buttons
        cls.select_records_for_iter()

    @classmethod
    def select_records_for_iter(cls):
        cls.destroy_summary_buttons()
        for button in cls.buttons:
            button.show()
        Const.main_window.next_word_button.hide()
        Const.main_window.display_details.hide()
        Const.main_window.word_info.hide()
        for button in cls.buttons:
            button.setStyleSheet(StyleSheets.FALLING_BUTTON_STYLE_SHEET)
        if len(cls.unused) == 0:
            print("end of batch")

            Const.current_batch += 1

            cls.unused = cls.game_record[
                         (Const.current_batch - 1) * Const.batch_size:Const.current_batch * Const.batch_size]

            cls.already_used = []
            cls.create_batch_summary()

            Const.main_window.next_batch_button.clicked.connect(lambda: cls.select_records_for_iter())
            Const.main_window.restart_batch_button.clicked.connect(lambda: cls.restart_batch())

            if len(cls.unused) == 0:
                cls.win_action()
            return

        cls.currently_correct = random.choice(cls.unused)
        cls.current_batch = cls.game_record[
                            (Const.current_batch - 1) * Const.batch_size:Const.current_batch * Const.batch_size]

        temp = cls.current_batch.copy()
        temp.remove(cls.currently_correct)
        if len(temp) < Const.iter_size - 1:
            cls.current_batch = cls.game_record[
                                (
                                        Const.current_batch - 1) * Const.batch_size - Const.iter_size:Const.current_batch * Const.batch_size]

            temp = cls.current_batch.copy()
            temp.remove(cls.currently_correct)

        cls.current_iter = random.choices(temp, k=Const.iter_size - 1)

        cls.unused.remove(cls.currently_correct)
        cls.already_used.append(cls.currently_correct)

        chosen_records = [*cls.current_iter, cls.currently_correct]
        random.shuffle(chosen_records)
        for button, iter_choice in zip(cls.buttons, chosen_records):
            button.ID = iter_choice.ID
            button.setText(asdict(iter_choice)[cls.compare_from])

        correct_answer_label_text = f"Pick up:\n {asdict(cls.currently_correct)[cls.compare_to]}"
        Const.main_window.answer_to_pick.setText(correct_answer_label_text)
        current_batch_and_iter_text = f"batch: {Const.current_batch}/{cls.number_of_batches} \n" \
                                      f" iter: {len(cls.already_used)}/{len(cls.unused) + len(cls.already_used)}"
        Const.main_window.batch_and_iter.setText(current_batch_and_iter_text)
        cls.update_sound_consts(record=cls.currently_correct)

    @classmethod
    def initiate_task(cls):
        if hasattr(Const.main_window, "task_attributes") and Const.main_window.task_attributes is not []:
            try:
                cls.kill_exercise_task()
            except RuntimeError:
                Const.main_window.task_attributes = []
                print("already Deleted")
        Const.current_batch = 1
        cls.game_record = [record for record in Const.parser.all_records
                           if record.ID in Const.main_window.all_selected_records]
        cls.current_batch = cls.game_record[0:Const.current_batch * Const.batch_size]
        cls.unused = cls.current_batch

        Const.main_window.hint_button.clicked.connect(lambda: cls.colour_buttons())
        Const.main_window.display_details.clicked.connect(lambda: cls.display_a_hint())
        Const.main_window.next_word_button.clicked.connect(lambda: cls.select_records_for_iter())

        Const.main_window.answer_to_pick = QLabel(Const.main_window)
        Const.main_window.answer_to_pick.setText("None")
        Const.main_window.answer_to_pick.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.answer_to_pick.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        Const.main_window.answer_to_pick.setAlignment(Qt.AlignCenter)
        Const.main_window.left_height_box.addWidget(Const.main_window.answer_to_pick, 0, 0, )
        Const.main_window.batch_and_iter = QLabel(Const.main_window)
        Const.main_window.batch_and_iter.setText("None")
        Const.main_window.batch_and_iter.setStyleSheet("color: rgb(255, 255, 255);")
        Const.main_window.batch_and_iter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        Const.main_window.batch_and_iter.setAlignment(Qt.AlignCenter)
        Const.main_window.left_height_box.addWidget(Const.main_window.batch_and_iter, 1, 0, )

        cls.number_of_batches = ceil(len(cls.game_record) / Const.batch_size)

        cls.create_buttons()

        print("intiation finished")
