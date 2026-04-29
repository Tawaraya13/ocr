from PySide6.QtWidgets import QToolBar
from PySide6.QtGui import QAction

class Toolbar(QToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        capture_action = QAction("Capture", self)
        capture_action.triggered.connect(self.parent.on_capture_clicked)
        self.addAction(capture_action)

        translate_action = QAction("Translate", self)
        translate_action.triggered.connect(self.parent.on_translate_clicked)
        self.addAction(translate_action)

        furigana_action = QAction("Furigana", self)
        furigana_action.triggered.connect(self.parent.on_furigana_clicked)
        self.addAction(furigana_action)
