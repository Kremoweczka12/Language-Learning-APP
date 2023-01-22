from utils.global_access_classes import ErrorDialog


def display_error_window(msg):
    dlg = ErrorDialog(msg)
    dlg.setWindowTitle("ERROR")
    dlg.exec_()
