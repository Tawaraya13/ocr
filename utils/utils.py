from PySide6.QtCore import QBuffer, QIODevice, QRect
from PySide6.QtGui import QGuiApplication
from PIL import Image
import pytesseract
import logging
import os
import time
import screenshot
import io
import re

logger = logging.getLogger(__name__)

class Utils:
    #apply new line to text
    @staticmethod
    def format_text(text, orientation):
        formattext = ""
        if orientation == 'vertical':
            for line in re.split(r'(?<=\.)', text):
                line = line.strip()
                if line:
                    formattext += f"{line}</br>"
        elif orientation == 'horizontal':
            for line in text.splitlines():
                formattext += f"<p>{line}</p>"
        return formattext

    def reconstruct_text(text):
        lines = text.split("\n")
        result = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                result.append("\n")  # paragraph break
                continue
            
            if result:
                prev = result[-1]
                
                # hyphenated word
                if prev.endswith("-"):
                    result[-1] = prev[:-1] + line
                    continue
                
                # check if should merge
                if (not prev.endswith(('.', '?', '!', ':', ';')) 
                    and line and line[0].islower()):
                    result[-1] += " " + line
                    continue
            
            result.append(line)
    
        return "\n".join(result)

    @staticmethod
    def save_image_in_temp_folder(image, postfix: str = "") -> None:
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
        image.save(file_path, "PNG")

    def _take_screenshots(self, delay: bool):
        if delay:
            # Timeout should be high enough for visible windows to completely hide windows before screenshot is taken, but low enough to not cause too much delay for user.
            time.sleep(0.5)
        screens = screenshot.capture() 

        if not screens:
            self.settings.setValue("has-screenshot-permission", False)
            raise RuntimeError("No screenshot taken!")

        for idx, image in enumerate(screens):
            Utils.save_image_in_temp_folder(image, postfix=f"_raw_screen{idx}")

        return screens

    def on_cropped(rect, image):
        screen = QGuiApplication.screenAt(rect.topLeft()) or QGuiApplication.primaryScreen()
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
        logging.info("Update clipboard and viewer")
        QGuiApplication.clipboard().setImage(final_image)
        Utils.save_image_in_temp_folder(image, postfix="_cropped")
        return final_image

    @staticmethod
    def pytesseractOCR(image, orientation='horizontal'):
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        image.save(buffer, "PNG")  # save QImage into buffer as PNG
        pil_image = Image.open(io.BytesIO(buffer.data()))
        if orientation == 'vertical':
            ocrtext = pytesseract.image_to_string(pil_image, lang='jpn_vert')
        elif orientation == 'horizontal':
            ocrtext = pytesseract.image_to_string(pil_image, lang='jpn')
        else:
            raise ValueError(f"Invalid orientation: {orientation}")
        print(ocrtext)
        return ocrtext