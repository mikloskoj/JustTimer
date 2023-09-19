import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle("Button Toggle Example")

        self.start_button = QPushButton("Start", self)
        self.start_button.setGeometry(200, 285, 55, 50)
        self.start_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.5); color: rgba(0, 0, 0, 0.7); border-radius: 3px;text-align: center;font-weight: bold; font-size: 9px;")
        self.start_button.clicked.connect(self.toggle_buttons)

        self.timer_button = QPushButton("Timer", self)
        self.timer_button.setGeometry(325, 325, 130, 20)
        self.timer_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); border-radius: 3px;text-align: right;font-weight: bold;font-size: 8px;")
        self.timer_button.clicked.connect(self.toggle_buttons)
        self.timer_button.hide()

    def toggle_buttons(self):
        # Check which button was clicked and toggle their visibility
        if self.sender() == self.start_button:
            self.start_button.hide()
            self.timer_button.show()
        elif self.sender() == self.timer_button:
            self.timer_button.hide()
            self.start_button.show()

def main():
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
