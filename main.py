
import sys
import time

from PySide6.QtWidgets import QApplication

from windows.pyside_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec_()
    start_time = time.time()
