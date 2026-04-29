from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QMenuBar

class MainMenu(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # Option menu
        option_list = self.addMenu("Option")

        # OCR Orientation submenu
        self.pytesseract_vertical_action = QAction("Vertical", self)
        self.pytesseract_vertical_action.setCheckable(True)
        self.pytesseract_vertical_action.setData('vertical')
        self.pytesseract_horizontal_action = QAction("Horizontal", self)
        self.pytesseract_horizontal_action.setCheckable(True)
        self.pytesseract_horizontal_action.setData('horizontal')
        self.pytesseract_horizontal_action.setChecked(True)

        group_ocr_orient = QActionGroup(self)
        group_ocr_orient.setExclusive(True)
        group_ocr_orient.addAction(self.pytesseract_vertical_action)
        group_ocr_orient.addAction(self.pytesseract_horizontal_action)
        group_ocr_orient.triggered.connect(self.parent.set_ocr_selection)

        ocr_orient_menu = option_list.addMenu("OCR Orientation")
        ocr_orient_menu.addAction(self.pytesseract_vertical_action)
        ocr_orient_menu.addAction(self.pytesseract_horizontal_action)

        # Translator submenu
        self.google_action = QAction("Google", self)
        self.google_action.setCheckable(True)
        self.google_action.setData('google')
        self.google_action.setChecked(True)

        group_translation = QActionGroup(self)
        group_translation.setExclusive(True)
        group_translation.addAction(self.google_action)
        group_translation.triggered.connect(self.parent.set_translator_selection)

        translator_menu = option_list.addMenu("Translator")
        translator_menu.addAction(self.google_action)

        #auto set translator selection to google on startup
        self.parent.set_translator_selection(self.google_action)
        self.parent.set_ocr_selection(self.pytesseract_horizontal_action)