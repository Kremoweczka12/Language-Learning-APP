
from utils.global_access_classes import Const


class BaseHandler:

    @staticmethod
    def kill_exercise_task(spare_loading_parts=False):
        for attribute in Const.main_window.task_attributes:
            if spare_loading_parts and attribute == Const.main_window.main_menu_box:
                continue
            try:
                attribute.deleteLater()
            except RuntimeError:
                print(f"attribute already destroyed")
        Const.main_window.task_attributes = []
