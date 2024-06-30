import os, sys
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QTimer, QTime, QEvent, QUrl
from PyQt6.QtGui import QColor, QPixmap, QPalette, QFont, QPainter, QBrush
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QMainWindow
from qframelesswindow import FramelessWindow, TitleBar, StandardTitleBar
from PyQt6.QtMultimedia import QSoundEffect
import time

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
        
    return os.path.join(base_path, relative_path)


class MenuHover(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setScaledContents(True)
        label_palette = self.palette()
        label_palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 200, 200))
        self.setPalette(label_palette)
        custom_font = QFont("JetBrains Mono", 100)
        self.setFont(custom_font)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setStyleSheet("QLabel:hover { color: white; }")  # Change color on hover

class CustomTitleBar(StandardTitleBar):
    """ Custom title bar """

    def __init__(self, parent):
        super().__init__(parent)

        # customize the style of title bar button
        self.minBtn.setHoverColor(Qt.GlobalColor.white)
        self.minBtn.setHoverBackgroundColor(QColor(0, 100, 182))
        self.minBtn.setPressedColor(Qt.GlobalColor.white)
        self.minBtn.setPressedBackgroundColor(QColor(54, 57, 65))

        # use qss to customize title bar button
        self.maxBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        """)

class Window(FramelessWindow):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.initUI()

    def initUI(self):

        self.setGeometry(100, 100, 700, 400)
        # change the default title bar if you like
        self.setTitleBar(CustomTitleBar(self))
        

        self.label = QLabel(self)
        self.label.setScaledContents(True)

# Set a background image for the window
        self.background_label = QLabel(self)
        self.background_label.setScaledContents(True)
        self.background_image = QPixmap(resource_path("background4_1100x400.png"))
        self.background_label.setPixmap(self.background_image)

        # Calculate the endValue for the animation based on the image width and window width
        self.animation_end_x = -self.background_image.width() + self.width()

        self.background_animation = QPropertyAnimation(self.background_label, b"pos", self)
        self.background_animation.setDuration(20000)  # Adjust the duration as needed
        self.background_animation.setStartValue(self.background_label.pos())
        self.background_animation.setEndValue(QPoint(self.animation_end_x, 0))

        self.background_animation.finished.connect(self.reverseBackgroundAnimation)
        self.background_animation.start()

        # --------------------
        self.label_title = QLabel(self)
        self.label_title.setScaledContents(True)
        self.label_title.setText("JustTimer")
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_palette = self.label_title.palette()
        label_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.label_title.setPalette(label_palette)
        custom_font = QFont("JetBrains Mono", 30)
        self.label_title.setFont(custom_font)
        self.label_title.move(35, 35)


        # DESC -------------------------------------
        self.label_desc = QLabel(self)
        self.label_desc.setScaledContents(True)
        self.label_desc.setText("Focus utility |")
        self.label_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_palette = self.label_desc.palette()
        label_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        self.label_desc.setPalette(label_palette)
        custom_font = QFont("JetBrains Mono", 10)
        self.label_desc.setFont(custom_font)
        self.label_desc.move(35, 85)


        # --------------------------------------        
        self.label_time = QLabel(self)
        self.label_time.setFont(QFont("JetBrains Mono", 10))
        self.label_time.setGeometry(163, 83, 100, 20)
        self.label_time.setStyleSheet("color: dark gray;") 

        self.timer = QTimer(self, interval=1000)
        self.timer.timeout.connect(self.update_time)
        self.timer.start()
        self.update_time()
        


# _____________ TIMER APP _____________


        self.running = False
        self.elapsed_time = 0
        self.start_time = 0


        self.timer_label = QLabel("00:00:00", self)
        self.timer_label.setFont(QFont("JetBrains Mono", 20))
        self.timer_label.setGeometry(37, 292, 250, 250)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.timer_label.setStyleSheet("color: white;") 
        self.timer_label.hide()

        self.timer_exit_button = QPushButton("X", self)
        self.timer_exit_button.setGeometry(240, 252, 15, 15)
        self.timer_exit_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.8); color: rgba(0, 0, 0, 0.3); border-radius: 7px;text-align: center;font-weight: bold; font-size: 10px;")
        self.timer_exit_button.clicked.connect(self.timer_exit_button_clicked)
        self.timer_exit_button.clicked = 0
        self.timer_exit_button.hide()


        self.start_button = QPushButton("Start", self)
        self.start_button.setGeometry(200, 285, 55, 50)
        self.start_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.4); color: rgba(0, 0, 0, 0.7); border-radius: 3px;text-align: center;font-weight: bold; font-size: 9px;")
        self.start_button.clicked.connect(self.timer_start_button_clicked)
        self.start_button.clicked = 0
        self.is_paused = False
        self.start_button.hide()


        self.reset_button = QPushButton("Reset", self)
        self.reset_button.setGeometry(200, 338, 55, 15)
        self.reset_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); color: rgba(255, 255, 255, 0.4); border-radius: 3px;text-align: center;font-weight: normal; font-size: 8px;")
        self.reset_button.clicked.connect(self.timer_reset_button_clicked)
        self.reset_button.clicked = 0
        self.reset_button.hide()

        # Timer TITLE
        self.label_timer_title = QLabel(self)
        self.label_timer_title.setScaledContents(True)
        self.label_timer_title.setText("")
        self.label_timer_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_timer_title.setStyleSheet("background-color: rgba(255, 255, 255, 0.8);color: rgba(255, 255, 255, 0.5);font-size: 7px; text-align: center;font-weight: normal;border-radius: 3px;")    
        self.label_timer_title.setPalette(label_palette)
        custom_font = QFont("JetBrains Mono", 7)
        self.label_timer_title.setFont(custom_font)
        self.label_timer_title.setGeometry(30, 270,225,12)
        self.label_timer_title.hide()


        self.timer_indicator = QLabel(self)
        self.timer_indicator.setScaledContents(True)
        self.timer_indicator.setText("")
        self.timer_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_indicator.setStyleSheet("background-color: rgba(255, 255, 255, 0.8);color: rgba(255, 255, 255, 0.5);font-size: 7px; text-align: center;font-weight: normal;border-radius: 3px;") 
        self.timer_indicator.setFont(custom_font)
        self.timer_indicator.setGeometry(30, 270,30,12)
        self.timer_indicator.hide()

        self.timer_indicator_2 = QLabel(self)
        self.timer_indicator_2.setScaledContents(True)
        self.timer_indicator_2.setText("")
        self.timer_indicator_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_indicator_2.setStyleSheet("background-color: rgba(255, 255, 255, 0.8);color: rgba(255, 255, 255, 0.5);font-size: 7px; text-align: center;font-weight: normal;border-radius: 3px;") 
        self.timer_indicator_2.setFont(custom_font)
        self.timer_indicator_2.setGeometry(150, 370, 10, 12)
        self.timer_indicator_2.hide()


        self.label_timer_background = QLabel(self)
        self.label_timer_background.setScaledContents(True)
        self.label_timer_background.setText("                                             ")
        self.label_timer_background.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_timer_background.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);color: white;border-radius: 3px;") 
        self.label_timer_background.setPalette(label_palette)
        custom_font = QFont("JetBrains Mono", 7)
        self.label_timer_background.setFont(custom_font)
        self.label_timer_background.setGeometry(30, 285, 167, 50)
        self.label_timer_background.hide()
        


        self.timer = QTimer(self, interval=1000)
        self.timer.timeout.connect(self.timer_update)
        self.timer.start()

        # TIMER -------------------------------
        self.timer_button = QPushButton("       Timer", self)
        self.timer_button.setGeometry(30, 375, 130, 25)
        self.timer_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); border-radius: 3px;text-align: left;font-weight: bold;font-size: 8px;")
        self.timer_button.clicked.connect(self.timer_button_click)
        self.timer_button.clicked = 0

        self.sound_effect = QSoundEffect()
        self.sound_effect.setSource(QUrl.fromLocalFile(resource_path("click.wav")))

        # Button Mouse Hover
        self.start_button.installEventFilter(self)
        self.timer_exit_button.installEventFilter(self)
        self.timer_button.installEventFilter(self)
        self.reset_button.installEventFilter(self) 

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timer_update)

        
        self.titleBar.raise_()


    def timer_button_click(self):

        self.sound_effect.play()

        if self.timer_button.clicked == 0:
            self.timer_button.setStyleSheet(
            "background-color: rgba(255, 255, 255, 1); color: black; border-radius: 3px;text-align: left;font-weight: bold;font-size: 8px;"
            )
            print("Button Clicked! Setting 'clicked' to 1.")
            self.timer_button.clicked = 1
            self.start_button.show()
            self.reset_button.show()
            self.timer_exit_button.show()
            self.timer_label.show()
            self.label_timer_title.show()
            self.label_timer_background.show()
            self.timer_indicator.show()
            
        else:
            self.timer_button.setStyleSheet(
            "background-color: rgba(255, 255, 255, 1); color: black; border-radius: 3px;text-align: left;font-weight: bold;font-size: 8px;"
            )
            print("Button Clicked Again! Setting 'clicked' to 0.")
            self.timer_button.clicked = 0
            self.start_button.hide()
            self.reset_button.hide()
            self.timer_exit_button.hide()
            self.timer_label.hide()
            self.label_timer_title.hide()
            self.label_timer_background.hide()
            self.timer_indicator.hide()
            self.timer_indicator_2.hide()

    
    def eventFilter(self, obj, event):
        if obj == self.timer_button:
            if event.type() == QEvent.Type.Enter:
                self.timer_button.setStyleSheet("background-color: rgba(255, 255, 255, 1); color: gray; border-radius: 3px;text-align: left;font-weight: bold;font-size: 8px;")
            elif event.type() == QEvent.Type.Leave:
                self.timer_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); color: rgba(255, 255, 255, 0.7); border-radius: 3px;text-align: left;font-weight: bold;font-size: 8px;")

        elif obj == self.timer_exit_button:
            if event.type() == QEvent.Type.Enter:
                self.timer_exit_button.setStyleSheet("background-color: #832f2f; color: rgba(255, 255, 255, 0.7); border-radius: 7px;text-align: center;font-weight: bold;font-size: 10px;")
            elif event.type() == QEvent.Type.Leave:
                self.timer_exit_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.8); color: rgba(0, 0, 0, 0.3); border-radius: 7px;text-align: center;font-weight: bold; font-size: 10px;")
        elif obj == self.start_button:
            if event.type() == QEvent.Type.Enter:
                self.start_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.6); color: rgba(0, 0, 0, 0.7); border-radius: 3px;text-align: center;font-weight: bold; font-size: 9px;")
            elif event.type() == QEvent.Type.Leave:
                self.start_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.4); color: rgba(0, 0, 0, 0.7); border-radius: 3px;text-align: center;font-weight: bold; font-size: 9px;")
        elif obj == self.reset_button:
            if event.type() == QEvent.Type.Enter:
                self.reset_button.setStyleSheet("background-color: #7a2929; color: rgba(255, 255, 255, 0.8); border-radius: 3px;text-align: center;font-weight: bold; font-size: 8px;")
            elif event.type() == QEvent.Type.Leave:
                self.reset_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.2); color: rgba(255, 255, 255, 0.4); border-radius: 3px;text-align: center;font-weight: normal; font-size: 8px;")
        return super().eventFilter(obj, event)

    

    def update_time(self):
        current_time = QTime.currentTime()
        time_text = current_time.toString("hh:mm:ss")
        self.label_time.setText(time_text)


    

    def timer_exit_button_clicked(self):
        self.sound_effect.play()
        self.timer_button.clicked = 0
        self.start_button.hide()
        self.reset_button.hide()
        self.timer_exit_button.hide()
        self.timer_label.hide()
        self.label_timer_title.hide()
        self.label_timer_background.hide()
        self.timer_indicator.hide()


    def timer_start_button_clicked(self):
        self.sound_effect.play()
        if self.is_paused:
            self.start_button.setText('Resume')
            self.start_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.6); color: rgba(0, 0, 0, 0.7); border-radius: 3px;text-align: center;font-weight: bold; font-size: 10px;")
            self.timer_indicator.setStyleSheet("background-color: #b8b8b8;color: rgba(255, 255, 255, 0.5);font-size: 7px; text-align: center;font-weight: normal;border-radius: 3px;") 
            self.timer_indicator_2.setStyleSheet("background-color: #b8b8b8;color: rgba(255, 255, 255, 0.5);font-size: 7px; text-align: center;font-weight: normal;border-radius: 3px;") 
            self.elapsed_time = time.time() - self.start_time
            self.running = False
            self.reset_button.show()

        else:
            self.start_button.setText('Pause')
            self.start_button.setStyleSheet("background-color: rgba(255, 255, 255, 0.6); color: #832f2f; border-radius: 3px;text-align: center;font-weight: bold; font-size: 10px;")
            self.timer_indicator.setStyleSheet("background-color: #567d40;color: rgba(255, 255, 255, 0.5);font-size: 7px; text-align: center;font-weight: normal;border-radius: 3px;")
            self.timer_indicator_2.setStyleSheet("background-color: #567d40;color: rgba(255, 255, 255, 0.5);font-size: 7px; text-align: center;font-weight: normal;border-radius: 3px;")
            self.start_time = time.time()
            self.start_time = time.time() - self.elapsed_time
            self.running = True
            self.timer.start(100)
            self.timer_indicator_2.show()
            self.reset_button.hide()

        self.is_paused = not self.is_paused


    def timer_reset_button_clicked(self):
        self.sound_effect.play()

        self.start_button.setStyleSheet(
                "background-color: rgba(255, 255, 255, 0.6); color: rgba(0, 0, 0, 0.7); border-radius: 3px;text-align: center;font-weight: bold; font-size: 10px;")
        self.timer_indicator.setStyleSheet(
                "background-color: #b8b8b8;color: rgba(255, 255, 255, 0.5);font-size: 7px; text-align: center;font-weight: normal;border-radius: 3px;")
        self.timer_indicator_2.setStyleSheet(
                "background-color: #b8b8b8;color: rgba(255, 255, 255, 0.5);font-size: 7px; text-align: center;font-weight: normal;border-radius: 3px;")

        self.running = False



        self.timer_update()
        self.elapsed_time = 0
        self.start_time = 0

        self.timer_indicator_2.hide()
        self.reset_button.hide()
        self.start_button.setText('Start')




        
    def timer_update(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
        hours, rem = divmod(int(self.elapsed_time), 3600)
        minutes, seconds = divmod(rem, 60)
        self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
       

    def reverseBackgroundAnimation(self):
    # Reverse the animation direction when it's finished
        if self.background_animation.direction() == QPropertyAnimation.Direction.Backward:
            self.background_animation.setDirection(QPropertyAnimation.Direction.Forward)
        else:
            self.background_animation.setDirection(QPropertyAnimation.Direction.Backward)
            self.background_animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.background_animation.start()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        length = min(self.width(), self.height())
        self.label.resize(length, length)
        self.label.move(
            self.width() // 2 - length // 2,
            self.height() // 2 - length // 2
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)    
    demo = Window()

    sound_effect = QSoundEffect()
    sound_effect.setSource(QUrl.fromLocalFile('click.wav'))

    demo.show()
    sys.exit(app.exec())
