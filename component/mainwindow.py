from PySide6.QtCore import QPoint,QThreadPool,QUrl,QRect
from PySide6.QtGui import QAction,QGuiApplication,QShortcut,QKeySequence
from PySide6.QtWidgets import QMainWindow,QVBoxLayout,QWidget,QMenu
from PySide6.QtWebEngineWidgets import QWebEngineView
from component.CaptureOverlay import CaptureOverlay
from furigana.furigana import return_html
from constant.constant import base_path, dicdir, capture_prompt, app_name
import urllib.parse
from utils.worker import Worker
from utils.utils import Utils
import os
from component.toolbar import Toolbar
from utils.translator import Translator
from component.menu import MainMenu

class main_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.translator = Translator()
        self.ocrselector = ""
        self.translator_selector = ""
        self.base_path = base_path
        self.dicdir = dicdir
        self.setWindowTitle(app_name)
        self.ocrtext = capture_prompt
        self.capture_overlays = []

        #main window
        self.viewtext = QWebEngineView()
        self.viewtext.setHtml(self.ocrtext)
        self._window_position = QPoint(0,0)   
        self.threadpool = QThreadPool()
        toolbarmenu = Toolbar(self)
        self.addToolBar(toolbarmenu)
        ss_shortcut = QShortcut(QKeySequence("Alt+Q"), self)
        ss_shortcut.activated.connect(self.on_capture_clicked)

        # Option menu
        self.main_menu = MainMenu(self)
        self.setMenuBar(self.main_menu)

        # Option menu Pytesseract OCR orientation
        layout = QVBoxLayout()
        layout.addWidget(self.viewtext)

        # Container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def set_translator_selection(self, action):
        self.translator_selector = action.data()
        print("Selected Translator:", self.translator_selector)

    def set_ocr_selection(self, action):
        self.ocrselector = action.data()
        print("Selected ocr orientation:", self.ocrselector)

    def on_furigana_clicked(self):
        self.loadingscreen()
        worker = Worker(self._furigana_worker)
        worker.signals.result.connect(self.write_to_user)
        self.threadpool.start(worker)

    def on_translate_clicked(self, e):
        self.loadingscreen()
        worker = Worker(self._translate_worker)
        worker.signals.result.connect(self.write_to_user)
        self.threadpool.start(worker)

    def on_capture_clicked(self):
        self.hide() #hide window before taking screenshot
        self.selection_state = {'begin': None, 'end': None, 'active': False}
        screenshot_img = Utils._take_screenshots(self,True)
        if not screenshot_img:
            print("Screenshot failed")
            return
        for screen, screenshot_img in zip(QGuiApplication.screens(),screenshot_img):
            overlay = CaptureOverlay(self,screenshot_img)
            overlay.show()  
            handle = overlay.windowHandle()
            if handle:
                handle.setScreen(screen)
            overlay.showMaximized()
            self.capture_overlays.append(overlay)

    def update_all_overlays(self):
        for overlay in self.capture_overlays:
            overlay.update()

    def finish_capture(self, image):
        if not self.selection_state.get('active'):
            return
        self.selection_state['active'] = False
        rect = QRect (
            self.selection_state['begin'],
            self.selection_state['end']
        ).normalized()
        for overlay in self.capture_overlays:
            overlay.close()
            self.capture_overlays = []
        self.showNormal()
        self.activateWindow()
        finalimage = Utils.on_cropped(rect,image)
        if finalimage is None:
            print("Cropping failed")
            return
        ocrtext = Utils.pytesseractOCR(finalimage, self.ocrselector)
        print(repr(ocrtext))
        if self.ocrselector == 'vertical':
            ocrtext = ocrtext.replace("\n", "").replace(" ", "")
        elif self.ocrselector == 'horizontal':
            ocrtext = Utils.reconstruct_text(ocrtext)
        self.ocrtext = ocrtext
        print(repr(self.ocrtext))
        self.write_to_user(ocrtext)

        
    def _translate_worker(self, progress_callback=None):
        if self.translator_selector == 'google':
            transltext = self.translator.translate(self.ocrtext, engine="google")
        else:
            raise ValueError(f"Unknown translator: {self.translator_selector}")
        print("Translated text:")
        print(transltext)
        return transltext
    
    def _furigana_worker(self, progress_callback=None):
        return return_html(self.ocrtext, self.dicdir)

    def write_to_user(self, text):
        format_text = Utils.format_text(text, self.ocrselector)
        self.viewtext.setHtml(format_text)
        print(format_text)

    def contextMenuEvent(self, e):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(e.globalPos())
    
    def loadingscreen(self):
        gif_path = os.path.join(self.base_path,"assets", "Loading_icon.gif")
        gif_url = QUrl.fromLocalFile(gif_path).toString()
        self.loading = f"""<div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
            <img src="{gif_url}" alt="Loading..."/>
        </div>"""
        self.viewtext.setHtml(self.loading)

