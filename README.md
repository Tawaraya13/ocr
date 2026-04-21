Manga OCR GUI NAME TO BE CHANGED
===============

Small PySide6 GUI that captures a screen region and runs OCR (pytesseract or manga_ocr) and optional translation/furigana.

Quick setup
-----------

1. Downloaad the file
2. Install mecab and choose UTF-8 https://github.com/ikegami-yukino/mecab/releases/download/v0.996.2/mecab-64-0.996.2.exe
3. Add mecab directory to PATH
4. Install Latest VC Redist https://learn.microsoft.com/id-id/cpp/windows/latest-supported-vc-redist?view=msvc-170
5. Download Tesseract and install the language needed https://docs.coro.net/featured/agent/install-tesseract-windows
6. Add Tesseract directory to PATH
7. Download Unidic to translate to furigana python -m unidic download

mecab instalation guide
https://github.com/mcho421/noj/blob/master/installing-mecab-python.md

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
