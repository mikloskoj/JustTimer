import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
from PyQt6.QtCore import Qt

class HoverLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("background-color: lightgray;")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def enterEvent(self, event):
        self.setStyleSheet("background-color: yellow;")
        event.accept()

    def leaveEvent(self, event):
        self.setStyleSheet("background-color: lightgray;")
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setGeometry(100, 100, 400, 200)

    label = HoverLabel("Hover over me!")
    label.setGeometry(100, 50, 200, 100)

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
