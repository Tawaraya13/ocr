from PySide6.QtWidgets import QApplication
from component.mainwindow import main_window
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = main_window()
    mainWindow.show()
    sys.exit(app.exec())