Japan OCR
===============

Small PySide6 GUI that captures a screen region and runs OCR (pytesseract or manga_ocr) and optional translation/furigana.

Quick setup
-----------

1. Create and activate a Python virtual environment (optional).
2. Install Python packages:
   pip install -r requirements.txt
3. Run the GUI:
   python mainwindow.py
   
Alternatively install through github

pip install git+https://github.com/Tawaraya13/ocr.git

Repository layout
-----------------
- `mainwindow.py` — main application UI and logic
- `CaptureOverlay.py` — screen selection overlay
- `screenshot/` — helpers used to take screenshots
- `requirements.txt` — Python dependencies

Notes
-----
- Tesseract must be installed on the host system for `pytesseract` to work.

Acknowledgements
-----
This project will not be possible without the MangaOcr model by Maciej Budyś and the Tesseract python wrapper by sirfz and the tesserocr contributors.

The software is licensed under GPLv3 (see LICENSE) and uses third party libraries that are distributed under their own terms (see LICENSE-3RD-PARTY).
