import sys
from PySide6.QtCore import Qt, QPoint, QRect, QTimer, QBuffer, QIODevice
from PySide6.QtGui import QAction, QGuiApplication, QActionGroup
from PySide6.QtWidgets import QApplication,QLabel,QMainWindow,QVBoxLayout,QWidget,QMenu,QToolBar 
from PySide6.QtWebEngineWidgets import QWebEngineView
import os
from manga_ocr import MangaOcr
import screenshot
import time
import logging
from CaptureOverlay import CaptureOverlay
from PIL import Image
from datetime import datetime
import io
from deep_translator import GoogleTranslator
from furigana.furigana import return_html
import pytesseract
from huggingface_hub import InferenceClient
from transformers import pipeline


logger = logging.getLogger(__name__)

class main_window(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.mocr = MangaOcr()
        self.gtranslator = GoogleTranslator
        self.ocrselector =1

        #main window
        self.setWindowTitle("My App")
        self.ocrtext ="please capture image"
        self.capture_overlays =[]
        #self.label = QLabel(self.ocrtext)
        #self.label.setAlignment(Qt.AlignCenter)
        #self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        #self.label.setTextFormat(Qt.TextFormat.RichText)
        self.viewtext = QWebEngineView()
        self.viewtext.setHtml(self.ocrtext)

        self._window_position = QPoint(0,0)   
         
        

        toolbar = QToolBar("Main Toolbar") 
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        capture_action = QAction("Capture", self)
        capture_action.triggered.connect(self.on_capture_clicked)

        toolbar.addAction(capture_action)

        translate_action = QAction("Translate", self)
        translate_action.triggered.connect(self.on_translate_clicked)

        toolbar.addAction(translate_action)

        furigana_action = QAction("Furigana", self)
        furigana_action.triggered.connect(self.on_furigana_clicked)

        toolbar.addAction(furigana_action)

        #option menu
        self.pytesseract_action = QAction("OCR Pytesseract", self)
        self.pytesseract_action.setCheckable(True)
        self.pytesseract_action.setData(1)

        self.mangaocr_action = QAction("OCR Manga_ocr", self)
        self.mangaocr_action.setCheckable(True)
        self.mangaocr_action.setData(2)
        
        group = QActionGroup(self)
        group.setExclusive(True)

        option_menu = self.menuBar()
        context_option = option_menu.addMenu("Option")
        context_option.addAction(self.pytesseract_action)
        context_option.addAction(self.mangaocr_action)

        group.addAction(self.pytesseract_action)
        self.pytesseract_action.setChecked(True)
        group.addAction(self.mangaocr_action)

        group.triggered.connect(self.set_ocr_selection)

        layout = QVBoxLayout()
        layout.addWidget(self.viewtext)
        #layout.addWidget(self.label) 

        #container
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def set_ocr_selection(self, action):
        self.ocrselector = action.data()
        print("Selected value:", self.ocrselector)

    def on_furigana_clicked(self, e):
        html_text = return_html(self.ocrtext)
        #self.label.setTextFormat(Qt.TextFormat.RichText)
        #self.label.setText(html_text)
        self.viewtext.setHtml(html_text)
        print(html_text)

    def on_translate_clicked(self, e):
        self.translate(self.ocrtext)

    def contextMenuEvent(self, e):
        context = QMenu(self)
        context.addAction(QAction("test 1", self))
        context.addAction(QAction("test 2", self))
        context.addAction(QAction("test 3", self))
        context.exec(e.globalPos())

    def on_capture_clicked(self,e):
        self.hide() #hide window before teking screenshot
        self.selection_state = {'begin': None, 'end': None, 'active': False}
        screenshot_img = self._take_screenshots(True)
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
        QTimer.singleShot(100, lambda: self.on_cropped(rect,image))

    def _take_screenshots(self, delay: bool):
        if delay:
            # Timeout should be high enough for visible windows to completely hide and
            time.sleep(0.5)
        screens = screenshot.capture() 

        if not screens:
            self.settings.setValue("has-screenshot-permission", False)
            raise RuntimeError("No screenshot taken!")

        for idx, image in enumerate(screens):
            self.save_image_in_temp_folder(image, postfix=f"_raw_screen{idx}")

        return screens    

    def save_image_in_temp_folder(self, image, postfix: str = "") -> None:
        """For debugging it can be useful to store the cropped image."""
        if logger.getEffectiveLevel() != logging.DEBUG:
             return

        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savedImages")
        os.makedirs(temp_dir, exist_ok=True)

        now_str = time.strftime("%Y-%m-%d_%H-%M-%S", time.gmtime())
        file_name = f"{now_str}{postfix}.png"
        file_path = os.path.join(temp_dir, file_name)

        logger.debug("Save debug image as %s", file_path)
        print("TYPE:", type(image))
        print("VALUE:", image is None)
        print(file_path)


    def on_cropped(self, rect, image):
        if rect.width() < 2 or rect.height() < 2:
            self.showNormal()
            self.activateWindow()
            return
        
        screen = QGuiApplication.screenAt(rect.topLeft()) or QGuiApplication.primaryScreen() # learn this
        dpr = screen.devicePixelRatio()
        screen_geometry = screen.geometry()
        crop_rect = QRect(
            int((rect.x() - screen_geometry.x()) * dpr),
            int((rect.y() - screen_geometry.y()) *dpr),
            int(rect.width() * dpr),
            int(rect.height() * dpr)
        )

        final_image = image.copy(crop_rect)
        # update clipboard and viewer
        logging.info("Updaate clipboard and viewer")
        QGuiApplication.clipboard().setImage(final_image)
        self.original_pixmap = final_image
        self.processImageforOCR(final_image)

    def processImageforOCR(self, image):
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "savedImages")
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(save_dir, f"capture_{timestamp}.png")
        success = image.save(file_path, "PNG")
        print("Save success:", success)
        if self.ocrselector == 1:
            print('running pytesseraact')
            self.pytesseractOCR(image)
        elif self.ocrselector == 2:
            print('running mangaocr')
            #self.mangaOCR(image, self.client)

    # def mangaOCR(self, image):
    #     buffer = QBuffer()
    #     buffer.open(QIODevice.WriteOnly)
    #     image.save(buffer, "PNG")  # save QImage into buffer as PNG
    #     pil_image = Image.open(io.BytesIO(buffer.data()))
    #     self.ocrtext = self.mocr(pil_image)
    #     self.viewtext.setHtml(self.ocrtext)
    #     #self.label.setText(self.ocrtext)
    #     print(self.ocrtext)

    def mangaOCR(self, image, client):
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")  # save QImage into buffer as PNG
        pil_image=Image.open(io.BytesIO(buffer.data()))
        result = self.pipe(pil_image)
        self.viewtext.setHtml(result)
        #self.label.setText(self.ocrtext)
        print(result)

    def pytesseractOCR(self, image):
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")  # save QImage into buffer as PNG
        pil_image = Image.open(io.BytesIO(buffer.data()))
        self.ocrtext = pytesseract.image_to_string(pil_image, lang='jpn')
        self.viewtext.setHtml(self.ocrtext)
        #self.label.setText(self.ocrtext)
        print(self.ocrtext)
        

    def translate(self, text):
        transltext = self.gtranslator(source='auto', target='en').translate(text)
        #self.label.setText(transltext)
        self.viewtext.setHtml(transltext)
        print(transltext)

app = QApplication(sys.argv)
mainWindow = main_window()
mainWindow.show()
app.exec()
