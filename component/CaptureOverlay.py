from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt, QRect


class CaptureOverlay(QWidget):
    def __init__(self, main_window, screenshot):
        super().__init__(None)
        self.main_window = main_window
        self.screenshot = screenshot
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window) # need to learn this aswell
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)

        

    def paintEvent(self, event):
        #selection coord stored in the global coord of the main window
        painter = QPainter(self)
        painter.drawImage(
            0,
            0,
            self.screenshot
        )
        state = self.main_window.selection_state
        if not state ['active']:
            painter.fillRect(self.rect(), QColor(0,0,0, 128))
            return

        # Create the global selection rectangle from the stored start/end point (probably gonna modify this)
        global_selection_rect = QRect(state['begin'], state['end']).normalized()

        #determine the portion of the selection that overlap with this screen
        local_reveal_rect = global_selection_rect.intersected(self.geometry())

        #translate the intersection rect to this widget local coordinates for painting
        local_reveal_rect.translate(-self.geometry().topLeft())

        #dim the entire widget area
        painter.fillRect(self.rect(), QColor(0,0,0, 128))
        if not local_reveal_rect.isEmpty():
            # clear the dimmed area within the slection to reveal the screen behind it
            painter.drawImage(
                local_reveal_rect,
                self.screenshot,
                local_reveal_rect.translated(self.geometry().topLeft())
            )
        painter.end()

    def mousePressEvent(self, event):
        state = self.main_window.selection_state
        state['active'] = True
        state['begin'] = event.globalPosition().toPoint()
        state['end'] = state['begin']
        self.main_window.update_all_overlays()

    def mouseMoveEvent(self, event):
        state = self.main_window.selection_state
        if state ['active']:
            state['end'] = event.globalPosition().toPoint()
            self.main_window.update_all_overlays()

    def mouseReleaseEvent(self, event):
        self.main_window.finish_capture(self.screenshot)