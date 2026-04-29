import sys, os

ocrselector = ['pytesseract']
translator_selector = ['google']
app_name = "Japan OCR"
app_ver = "0.5"
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
base_path = getattr(sys, '_MEIPASS', PROJECT_ROOT)
dicdir = os.path.join(base_path, 'unidic', 'dicdir')
capture_prompt = "<div style=\"display: flex; justify-content: center; align-items: center; height: 100vh;\"><p style=\"margin: 0;\">Click the Capture button or use Alt + Q</p></div>"