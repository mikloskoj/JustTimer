import os, sys, time
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QTime, QEvent, QSequentialAnimationGroup, QUrl, QEasingCurve, pyqtProperty, QAbstractAnimation, QSize, QPauseAnimation, QRectF
from PyQt6.QtGui import QColor, QPixmap, QPalette, QFont, QIcon, QRegion, QPainterPath, QPainter
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QLineEdit, QListWidget, QListWidgetItem, QGraphicsBlurEffect
from PyQt6.QtMultimedia import QSoundEffect
from qframelesswindow import FramelessWindow, StandardTitleBar

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Nové widgety s dynamickou barvou textu a glow efektem ---
class HoverLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._textOpacity = 1
        self.base_color = (255, 255, 255)
        self.updateStyleSheet()
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)
        self.shadow.setOffset(0)
        self.shadow.setColor(QColor(255, 255, 255))
        self.setGraphicsEffect(self.shadow)
        
    def updateStyleSheet(self):
        r, g, b = self.base_color
        self.setStyleSheet(f"color: rgba({r}, {g}, {b}, {self._textOpacity});")
    
    def getTextOpacity(self):
        return self._textOpacity
    
    def setTextOpacity(self, value):
        self._textOpacity = value
        self.updateStyleSheet()
    
    textOpacity = pyqtProperty(float, fget=getTextOpacity, fset=setTextOpacity)

class HoverLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._textOpacity = 0.5
        self.base_color = (255, 255, 255)
        self.updateStyleSheet()
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(0)
        self.shadow.setOffset(0)
        self.shadow.setColor(QColor(255, 255, 255))
    
    def updateStyleSheet(self):
        r, g, b = self.base_color
        self.setStyleSheet(
            f"background-color: rgba(255, 255, 255, 0);"
            f" color: rgba({r}, {g}, {b}, {self._textOpacity});"
            " border: none; font: 20px 'Roboto';"
        )
    
    def getTextOpacity(self):
        return self._textOpacity
    
    def setTextOpacity(self, value):
        self._textOpacity = value
        self.updateStyleSheet()
    
    textOpacity = pyqtProperty(float, fget=getTextOpacity, fset=setTextOpacity)

# --- Původní widgety a třídy ---
class AnimatedButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._flashValue = 1
        self.pressed_bg_alpha = 1.0
        self.default_bg_alpha = 0.0
        self.pressed_text_color = (0, 0, 0)
        self.default_text_color = (255, 255, 255)
        self.default_text_alpha = 1
        self.animation = QPropertyAnimation(self, b"flashValue")
        self.animation.setDuration(500)
        self.setFlashValue(0.0)
        self._fade_timer = None

    def getFlashValue(self):
        return self._flashValue

    def setFlashValue(self, value):
        self._flashValue = value
        current_alpha = self.default_bg_alpha + (self.pressed_bg_alpha - self.default_bg_alpha) * value
        current_r = int(self.default_text_color[0] + (self.pressed_text_color[0] - self.default_text_color[0]) * value)
        current_g = int(self.default_text_color[1] + (self.pressed_text_color[1] - self.default_text_color[1]) * value)
        current_b = int(self.default_text_color[2] + (self.pressed_text_color[2] - self.default_text_color[2]) * value)
        current_text_alpha = self.default_text_alpha + (1 - self.default_text_alpha) * value
        self.setStyleSheet(
            f"background-color: rgba(255, 255, 255, {current_alpha});"
            f" color: rgba({current_r}, {current_g}, {current_b}, {current_text_alpha});"
            " border-radius: 3px; text-align: center; font-weight: bold; font-size: 8px;"
        )

    flashValue = pyqtProperty(float, fget=getFlashValue, fset=setFlashValue)

    def flash(self):
        if self.animation.state() == QAbstractAnimation.State.Running:
            self.animation.stop()
        self.animation.setStartValue(self._flashValue)
        self.animation.setEndValue(0.0)
        self.animation.start()

    def enterEvent(self, event):
        if self._fade_timer is not None:
            self._fade_timer.stop()
            self._fade_timer = None
        self.animation.stop()
        self.setFlashValue(0.4)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._fade_timer = QTimer(self)
        self._fade_timer.setSingleShot(True)
        self._fade_timer.timeout.connect(self.flash)
        self._fade_timer.start(500)
        super().leaveEvent(event)

# --- Nová třída pro tlačítka s zaoblenými rohy ---
class RoundedAnimatedButton(AnimatedButton):
    def setFlashValue(self, value):
        self._flashValue = value
        current_alpha = self.default_bg_alpha + (self.pressed_bg_alpha - self.default_bg_alpha) * value
        current_r = int(self.default_text_color[0] + (self.pressed_text_color[0] - self.default_text_color[0]) * value)
        current_g = int(self.default_text_color[1] + (self.pressed_text_color[1] - self.default_text_color[1]) * value)
        current_b = int(self.default_text_color[2] + (self.pressed_text_color[2] - self.default_text_color[2]) * value)
        current_text_alpha = self.default_text_alpha + (1 - self.default_text_alpha) * value
        self.setStyleSheet(
            f"background-color: rgba(255, 255, 255, {current_alpha});"
            f" color: rgba({current_r}, {current_g}, {current_b}, {current_text_alpha});"
            " border-radius: 3px; text-align: center; font-weight: bold; font-size: 8px;"
        )

class MenuHover(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setScaledContents(True)
        label_palette = self.palette()
        label_palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 200, 200))
        self.setPalette(label_palette)
        custom_font = QFont("Roboto", 100)
        self.setFont(custom_font)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setStyleSheet("QLabel:hover { color: white; }")

class CustomTitleBar(StandardTitleBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.minBtn.setHoverColor(Qt.GlobalColor.white)
        self.minBtn.setHoverBackgroundColor(QColor(0, 100, 182))
        self.minBtn.setPressedColor(Qt.GlobalColor.white)
        self.minBtn.setPressedBackgroundColor(QColor(54, 57, 65))
        self.maxBtn.setStyleSheet("""
            TitleBarButton {
                qproperty-hoverColor: white;
                qproperty-hoverBackgroundColor: rgb(0, 100, 182);
                qproperty-pressedColor: white;
                qproperty-pressedBackgroundColor: rgb(54, 57, 65);
            }
        """)

# --- Hlavní okno s timerem, vstupem a animacemi při hoveru ---
class Window(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # Nastavení atributu pro průhledné pozadí, které bude následně malováno vlastním paintEvent()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.current_background = 0  # index aktuálního pozadí (0 až 5)
        self.hover_animations = []
        self.running = False         # Indikuje, zda timer běží
        self.timer_active = False    # Indikuje, zda byl timer spuštěn
        self.elapsed_time = 0
        self.start_time = 0
        # --- NOVÉ: kumulativní čas ---
        self.total_time = 0
        self.cumulative_time_label = HoverLabel("00:00:00", self)
        self.cumulative_time_label.setFont(QFont("Roboto", 10))
        self.cumulative_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cumulative_time_label.hide()  # skryjeme ji na začátku
        self.initUI()

    # Metoda pro změnu stavu bookmark tlačítka
    def updateBookmarkButtonState(self, text):
        if text.strip() == "":
            self.bookmark_button.setEnabled(False)
        else:
            self.bookmark_button.setEnabled(True)

    def initUI(self):
        self.setGeometry(100, 100, 700, 1000)
        self.setTitleBar(CustomTitleBar(self))

        self.label = QLabel(self)
        self.label.setScaledContents(True)

        # --- Pozadí ---
        # Background 1
        self.background_label1 = QLabel(self)
        self.background_label1.setScaledContents(True)
        self.pixmap1 = QPixmap(resource_path("background_1.png"))
        self.background_label1.setPixmap(self.pixmap1)
        self.background_label1.move(0, self.height() - self.pixmap1.height())
        self.background_label1.show()

        # Background 2
        self.background_label2 = QLabel(self)
        self.background_label2.setScaledContents(True)
        self.pixmap2 = QPixmap(resource_path("background_2.png"))
        self.background_label2.setPixmap(self.pixmap2)
        self.background_label2.move(0, self.height() - self.pixmap2.height())
        self.background_label2.hide()

        # Background 3
        self.background_label3 = QLabel(self)
        self.background_label3.setScaledContents(True)
        self.pixmap3 = QPixmap(resource_path("background_3.png"))
        self.background_label3.setPixmap(self.pixmap3)
        self.background_label3.move(0, self.height() - self.pixmap3.height())
        self.background_label3.hide()

        # --- Nové backgroundy ---
        # Background 4
        self.background_label4 = QLabel(self)
        self.background_label4.setScaledContents(True)
        self.pixmap4 = QPixmap(resource_path("background_4.png"))
        self.background_label4.setPixmap(self.pixmap4)
        self.background_label4.move(0, self.height() - self.pixmap4.height())
        self.background_label4.hide()

        # Background 5
        self.background_label5 = QLabel(self)
        self.background_label5.setScaledContents(True)
        self.pixmap5 = QPixmap(resource_path("background_5.png"))
        self.background_label5.setPixmap(self.pixmap5)
        self.background_label5.move(0, self.height() - self.pixmap5.height())
        self.background_label5.hide()

        # Background 6
        self.background_label6 = QLabel(self)
        self.background_label6.setScaledContents(True)
        self.pixmap6 = QPixmap(resource_path("background_6.png"))
        self.background_label6.setPixmap(self.pixmap6)
        self.background_label6.move(0, self.height() - self.pixmap6.height())
        self.background_label6.hide()

        # --- Vytvoření průsvitné vrstvy (světle bílá) s opacity efektem ---
        self.overlay_layer = QLabel(self)
        self.overlay_layer.setStyleSheet("background-color: rgba(0, 0, 0, 0.8);")
        self.overlay_layer.setGeometry(0, 0, self.width(), self.height())
        self.overlay_layer.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.overlay_effect = QGraphicsOpacityEffect(self.overlay_layer)
        self.overlay_layer.setGraphicsEffect(self.overlay_effect)
        self.overlay_effect.setOpacity(0)
        self.overlay_layer.hide()

        # --- Animace pozadí ---
        self.animForward1 = QPropertyAnimation(self.background_label1, b"pos", self)
        self.animBackward1 = QPropertyAnimation(self.background_label1, b"pos", self)
        self.setupAnimation(self.pixmap1, self.animForward1, self.animBackward1)
        self.anim_group1 = QSequentialAnimationGroup(self)
        self.anim_group1.addAnimation(self.animForward1)
        self.anim_group1.addAnimation(self.animBackward1)
        self.anim_group1.setLoopCount(-1)
        self.anim_group1.start()

        self.animForward2 = QPropertyAnimation(self.background_label2, b"pos", self)
        self.animBackward2 = QPropertyAnimation(self.background_label2, b"pos", self)
        self.setupAnimation(self.pixmap2, self.animForward2, self.animBackward2)
        self.anim_group2 = QSequentialAnimationGroup(self)
        self.anim_group2.addAnimation(self.animForward2)
        self.anim_group2.addAnimation(self.animBackward2)
        self.anim_group2.setLoopCount(-1)
        self.anim_group2.start()

        self.animForward3 = QPropertyAnimation(self.background_label3, b"pos", self)
        self.animBackward3 = QPropertyAnimation(self.background_label3, b"pos", self)
        self.setupAnimation(self.pixmap3, self.animForward3, self.animBackward3)
        self.anim_group3 = QSequentialAnimationGroup(self)
        self.anim_group3.addAnimation(self.animForward3)
        self.anim_group3.addAnimation(self.animBackward3)
        self.anim_group3.setLoopCount(-1)
        self.anim_group3.start()

        self.animForward4 = QPropertyAnimation(self.background_label4, b"pos", self)
        self.animBackward4 = QPropertyAnimation(self.background_label4, b"pos", self)
        self.setupAnimation(self.pixmap4, self.animForward4, self.animBackward4)
        self.anim_group4 = QSequentialAnimationGroup(self)
        self.anim_group4.addAnimation(self.animForward4)
        self.anim_group4.addAnimation(self.animBackward4)
        self.anim_group4.setLoopCount(-1)
        self.anim_group4.start()

        self.animForward5 = QPropertyAnimation(self.background_label5, b"pos", self)
        self.animBackward5 = QPropertyAnimation(self.background_label5, b"pos", self)
        self.setupAnimation(self.pixmap5, self.animForward5, self.animBackward5)
        self.anim_group5 = QSequentialAnimationGroup(self)
        self.anim_group5.addAnimation(self.animForward5)
        self.anim_group5.addAnimation(self.animBackward5)
        self.anim_group5.setLoopCount(-1)
        self.anim_group5.start()

        self.animForward6 = QPropertyAnimation(self.background_label6, b"pos", self)
        self.animBackward6 = QPropertyAnimation(self.background_label6, b"pos", self)
        self.setupAnimation(self.pixmap6, self.animForward6, self.animBackward6)
        self.anim_group6 = QSequentialAnimationGroup(self)
        self.anim_group6.addAnimation(self.animForward6)
        self.anim_group6.addAnimation(self.animBackward6)
        self.anim_group6.setLoopCount(-1)
        self.anim_group6.start()

        # Pauza animací na začátku
        self.anim_group1.pause()
        self.anim_group2.pause()
        self.anim_group3.pause()
        self.anim_group4.pause()
        self.anim_group5.pause()
        self.anim_group6.pause()

        self.toggleButton = AnimatedButton("", self)
        self.toggleButton.setIcon(QIcon(resource_path("picture-white.png")))
        self.toggleButton.setIconSize(QSize(18, 18))
        self.toggleButton.setGeometry(265, 375, 25, 25)
        self.toggleButton.clicked.connect(self.toggle_background)

        self.current_resolution_index = 0
        self.resolutions = [(900, 400), (400, 400), (700, 100)]
        self.resolutionToggleButton = AnimatedButton("", self)
        self.resolutionToggleButton.setIcon(QIcon(resource_path("resize-white.png")))
        self.resolutionToggleButton.setIconSize(QSize(18, 18))
        self.resolutionToggleButton.setGeometry(265, 375, 25, 25)
        self.resolutionToggleButton.clicked.connect(self.toggle_resolution)

        self.label_title = QLabel(self)
        self.label_title.setScaledContents(True)
        self.label_title.setText("JustTimer")
        self.label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_title.setStyleSheet("color: white;")
        custom_font = QFont("Roboto", 30)
        self.label_title.setFont(custom_font)
        self.label_title.move(35, 35)

        self.label_desc = QLabel(self)
        self.label_desc.setScaledContents(True)
        self.label_desc.setText("Focus utility |")
        self.label_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_desc.setStyleSheet("color: white;")
        custom_font = QFont("Roboto", 10)
        self.label_desc.setFont(custom_font)
        self.label_desc.move(35, 85)

        self.label_time = QLabel(self)
        self.label_time.setFont(QFont("Roboto", 10))
        self.label_time.setGeometry(150, 83, 100, 20)
        self.label_time.setStyleSheet("color: white;")

        self.clock_timer = QTimer(self, interval=1000)
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start()
        self.update_time()

        self.timer_label = HoverLabel("00:00:00", self)
        self.timer_label.setFont(QFont("Roboto", 60))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.hide()

        self.task_input = HoverLineEdit(self)
        self.task_input.setPlaceholderText("Na čem pracuješ? ...")
        self.task_input.setMaxLength(50)
        self.task_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.task_input.hide()
        self.task_input.textChanged.connect(self.updateBookmarkButtonState)

        self.bookmark_button = AnimatedButton("", self)
        self.bookmark_button.setIcon(QIcon(resource_path("bookmark-white.png")))
        self.bookmark_button.setIconSize(QSize(18, 18))
        self.bookmark_button.clicked.connect(self.activate_task)
        self.bookmark_button.hide()

        self.active_task_label = HoverLabel("", self)
        self.active_task_label.setFont(QFont("Roboto", 20))
        self.active_task_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.active_task_label.hide()

        self.reset_button = AnimatedButton("", self)
        self.reset_button.setIcon(QIcon(resource_path("eraser-white.png")))
        self.reset_button.setIconSize(QSize(18, 18))
        self.reset_button.setGeometry(195, 375, 25, 25)
        self.reset_button.clicked.connect(self.timer_reset_button_clicked)
        self.reset_button.hide()

        self.pause_button = AnimatedButton("", self)
        self.pause_button.setIcon(QIcon(resource_path("pause-white.png")))
        self.pause_button.setIconSize(QSize(18, 18))
        self.pause_button.setGeometry(165, 375, 25, 25)
        self.pause_button.clicked.connect(self.pause_button_clicked)
        self.pause_button.hide()

        self.start_button = AnimatedButton("", self)
        self.start_button.setIcon(QIcon(resource_path("play-white.png")))
        self.start_button.setIconSize(QSize(18, 18))
        self.start_button.setGeometry(165, 375, 25, 25)
        self.start_button.clicked.connect(self.start_button_clicked)
        self.start_button.hide()

        self.timer_button = RoundedAnimatedButton("", self)
        self.timer_button.setIcon(QIcon(resource_path("hourglass-start-white.png")))
        self.timer_button.setIconSize(QSize(28, 28))
        self.timer_button.clicked.connect(self.timer_button_click)
        self.timer_button.show()

        self.timer_button_sound = QSoundEffect()
        self.timer_button_sound.setSource(QUrl.fromLocalFile(resource_path("Menu Notification.wav")))

        self.task_completed_button = AnimatedButton("", self)
        self.task_completed_button.setIcon(QIcon(resource_path("check-white.png")))
        self.task_completed_button.setIconSize(QSize(18, 18))
        self.task_completed_button.clicked.connect(self.add_task_to_list)
        self.task_completed_button.hide()

        self.task_list = QListWidget(self)
        self.task_list.setStyleSheet("background-color: rgba(255, 255, 255, 0); font-size: 12px; color: rgba(255, 255, 255, 0.6); border: none;")
        self.task_list.hide()

        self.label_timer_background = QLabel(self)
        self.label_timer_background.setScaledContents(True)
        self.label_timer_background.setText("                                        ")
        self.label_timer_background.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label_timer_background.setStyleSheet("background-color: rgba(255, 255, 255, 0); color: white; border-radius: 10px;")
        self.label_timer_background.move(30, 150)
        self.label_timer_background.hide()

        self.timer_update_timer = QTimer(self, interval=1000)
        self.timer_update_timer.timeout.connect(self.timer_update)
        self.timer_update_timer.start()

        self.indicator = QLabel(self)
        self.indicator.setFixedSize(20, 20)
        self.indicator.setStyleSheet("background-color: rgba(255, 255, 255, 0.8); border-radius: 10px;")
        shadow = QGraphicsDropShadowEffect(self.indicator)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(255, 255, 255))
        shadow.setOffset(0)
        self.indicator.setGraphicsEffect(shadow)
        self.indicator.hide()
        
        self.sound_effect = QSoundEffect()
        self.sound_effect.setSource(QUrl.fromLocalFile(resource_path("click.wav")))

        self.titleBar.raise_()
        self.animate_startup_labels()

        self.control_buttons = [self.resolutionToggleButton, self.toggleButton, self.pause_button, self.start_button, self.reset_button, self.timer_button, self.task_completed_button, self.bookmark_button, self.task_list]
        self.update_all_label_text_colors()

    def paintEvent(self, event):
        # Vlastní vykreslení okna s hladkými zakulacenými rohy
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        path = QPainterPath()
        # Nastavení zakulaceného obdélníku; uprav hodnoty 20 podle potřeby
        path.addRoundedRect(QRectF(rect), 30, 30)
        # Například vyplň okno tmavým pozadím; uprav barvu dle potřeby
        painter.fillPath(path, QColor(30, 30, 30, 255))

    def fade_in_overlay(self, duration=500):
        self.overlay_layer.show()
        self.fade_in_anim = QPropertyAnimation(self.overlay_effect, b"opacity", self)
        self.fade_in_anim.setDuration(duration)
        self.fade_in_anim.setStartValue(self.overlay_effect.opacity())
        self.fade_in_anim.setEndValue(0.3)
        self.fade_in_anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def fade_out_overlay(self, duration=500):
        self.fade_out_anim = QPropertyAnimation(self.overlay_effect, b"opacity", self)
        self.fade_out_anim.setDuration(duration)
        self.fade_out_anim.setStartValue(self.overlay_effect.opacity())
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.finished.connect(self.overlay_layer.hide)
        self.fade_out_anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)

    def get_current_background_label(self):
        if self.current_background == 0:
            return self.background_label1
        elif self.current_background == 1:
            return self.background_label2
        elif self.current_background == 2:
            return self.background_label3
        elif self.current_background == 3:
            return self.background_label4
        elif self.current_background == 4:
            return self.background_label5
        elif self.current_background == 5:
            return self.background_label6

    def update_all_button_icons(self):
        if self.current_background in (0, 3, 4, 5):
            picture_icon = QIcon(resource_path("picture-white.png"))
            resize_icon = QIcon(resource_path("resize-white.png"))
            eraser_icon = QIcon(resource_path("eraser-white.png"))
            hourglass_icon = QIcon(resource_path("hourglass-start-white.png"))
            check_icon = QIcon(resource_path("check-white.png"))
            bookmark_icon = QIcon(resource_path("bookmark-white.png"))
            play_icon = QIcon(resource_path("play-white.png"))
            pause_icon = QIcon(resource_path("pause-white.png"))
        else:
            picture_icon = QIcon(resource_path("picture.png"))
            resize_icon = QIcon(resource_path("resize.png"))
            eraser_icon = QIcon(resource_path("eraser.png"))
            hourglass_icon = QIcon(resource_path("hourglass-start.png"))
            check_icon = QIcon(resource_path("check.png"))
            bookmark_icon = QIcon(resource_path("bookmark.png"))
            play_icon = QIcon(resource_path("play.png"))
            pause_icon = QIcon(resource_path("pause.png"))
    
        self.toggleButton.setIcon(picture_icon)
        self.resolutionToggleButton.setIcon(resize_icon)
        self.reset_button.setIcon(eraser_icon)
        self.timer_button.setIcon(hourglass_icon)
        self.task_completed_button.setIcon(check_icon)
        self.bookmark_button.setIcon(bookmark_icon)
        self.start_button.setIcon(play_icon)
        self.pause_button.setIcon(pause_icon)

    def update_all_label_text_colors(self):
        if self.current_background in (0, 2, 3, 4, 5):
            text_color = "white"
            rgb = (255, 255, 255)
            task_text_rgba = "rgba(255, 255, 255, 0.6)"
        else:
            text_color = "black"
            rgb = (0, 0, 0)
            task_text_rgba = "rgba(0, 0, 0, 0.6)"
        self.label_title.setStyleSheet(f"color: {text_color};")
        self.label_desc.setStyleSheet(f"color: {text_color};")
        self.label_time.setStyleSheet(f"color: {text_color};")
        self.label_timer_background.setStyleSheet(f"background-color: rgba(255, 255, 255, 0); color: {text_color}; border-radius: 3px;")
        self.timer_label.base_color = rgb
        self.timer_label.updateStyleSheet()
        self.task_input.base_color = rgb
        self.task_input.updateStyleSheet()
        self.active_task_label.base_color = rgb
        self.active_task_label.updateStyleSheet()
        self.cumulative_time_label.base_color = rgb
        self.cumulative_time_label.updateStyleSheet()
        self.task_list.setStyleSheet(
            f"background-color: rgba(255, 255, 255, 0); font-size: 12px; color: {task_text_rgba}; border: none;"
        )

    def animate_startup_labels(self):
        self.startup_animations = []
        for label in [self.label_title, self.label_desc, self.label_time]:
            effect = QGraphicsOpacityEffect(label)
            label.setGraphicsEffect(effect)
            effect.setOpacity(0)
            seq_group = QSequentialAnimationGroup(self)
            fade_in = QPropertyAnimation(effect, b"opacity")
            fade_in.setDuration(6000)
            fade_in.setStartValue(0)
            fade_in.setEndValue(1)
            pause = QPauseAnimation(5000)
            fade_out = QPropertyAnimation(effect, b"opacity")
            fade_out.setDuration(5000)
            fade_out.setStartValue(1)
            fade_out.setEndValue(0)
            seq_group.addAnimation(fade_in)
            seq_group.addAnimation(pause)
            seq_group.addAnimation(fade_out)
            seq_group.start()
            self.startup_animations.append(seq_group)

    def setupAnimation(self, pixmap, animForward, animBackward):
        start_pos = QPoint(0, self.height() - pixmap.height())
        end_pos = QPoint(self.width() - pixmap.width(), 0)
        animForward.setDuration(80000)
        animForward.setEasingCurve(QEasingCurve.Type.Linear)
        animForward.setStartValue(start_pos)
        animForward.setEndValue(end_pos)
        animBackward.setDuration(80000)
        animBackward.setEasingCurve(QEasingCurve.Type.Linear)
        animBackward.setStartValue(end_pos)
        animBackward.setEndValue(start_pos)

    def toggle_background(self):
        self.sound_effect.play()
        self.toggleButton.flash()
        self.current_background = (self.current_background + 1) % 6
        self.background_label1.hide()
        self.background_label2.hide()
        self.background_label3.hide()
        self.background_label4.hide()
        self.background_label5.hide()
        self.background_label6.hide()
        if self.current_background == 0:
            self.background_label1.show()
        elif self.current_background == 1:
            self.background_label2.show()
        elif self.current_background == 2:
            self.background_label3.show()
        elif self.current_background == 3:
            self.background_label4.show()
        elif self.current_background == 4:
            self.background_label5.show()
        elif self.current_background == 5:
            self.background_label6.show()
        self.update_all_button_icons()
        self.update_all_label_text_colors()

    def toggle_resolution(self):
        self.sound_effect.play()
        self.resolutionToggleButton.flash()
        self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
        new_width, new_height = self.resolutions[self.current_resolution_index]
        self.setGeometry(self.x(), self.y(), new_width, new_height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Aktualizace overlay vrstvy a dalších widgetů
        self.overlay_layer.setGeometry(0, 0, self.width(), self.height())
        self.label_title.adjustSize()
        self.label_title.move((self.width() - self.label_title.width()) // 2, 150)
        self.label_desc.adjustSize()
        self.label_time.adjustSize()
        spacing = 10
        total_width = self.label_desc.width() + spacing + self.label_time.width()
        start_x = (self.width() - total_width) // 2
        self.label_desc.move(start_x, 200)
        self.label_time.move(start_x + self.label_desc.width() + spacing, 200)
        self.timer_label.adjustSize()
        self.timer_label.move((self.width() - self.timer_label.width()) // 2,
                              (self.height() - self.timer_label.height()) // 2)
        self.timer_button.setGeometry(self.timer_label.geometry())
        self.task_input.setGeometry((self.width() - 300) // 2,
                                    self.timer_label.y() + self.timer_label.height() + 10,
                                    300, 50)
        self.task_list.setGeometry((self.width() - 300) // 2,
                                   self.task_input.y() + self.task_input.height() + 10,
                                   300, 200)
        self.cumulative_time_label.setGeometry((self.width() - 10) // 2,
                                               self.timer_label.y(),
                                               180, 10)
        if self.active_task_label.isVisible():
            self.active_task_label.setGeometry((self.width() - 300) // 2,
                                               self.timer_label.y() + self.timer_label.height() + 10,
                                               300, 50)
        self.task_completed_button.setGeometry(self.task_input.x() + self.task_input.width() + 10,
                                               self.task_input.y(), 50, 50)
        self.indicator.move(self.width() - self.indicator.width() - 20, 50)
        btn_height = 35
        btn_spacing = 3
        total_btn_width = 35 + btn_spacing + 35 + btn_spacing + 35 + btn_spacing + 35 + btn_spacing + 130
        x_start = (self.width() - total_btn_width) // 2
        new_y = self.timer_label.y() - btn_height - 10
        self.resolutionToggleButton.setGeometry(x_start, new_y, 35, btn_height)
        self.toggleButton.setGeometry(x_start + 35 + btn_spacing, new_y, 35, btn_height)
        self.start_button.setGeometry(x_start + 35 + btn_spacing + 35 + btn_spacing, new_y, 35, btn_height)
        self.pause_button.setGeometry(x_start + 35 + btn_spacing + 35 + btn_spacing, new_y, 35, btn_height)
        self.reset_button.setGeometry(x_start + 35 + btn_spacing + 35 + btn_spacing + 35 + btn_spacing, new_y, 35, btn_height)
        self.bookmark_button.setGeometry(self.task_input.x() + self.task_input.width() + 10,
                                         self.task_input.y(), 50, 50)
        
        # Aktualizace animací pozadí, aby se přepočítaly nové start a end hodnoty
        # Background 1
        start_pos = QPoint(0, self.height() - self.pixmap1.height())
        end_pos = QPoint(self.width() - self.pixmap1.width(), 0)
        self.animForward1.setStartValue(start_pos)
        self.animForward1.setEndValue(end_pos)
        self.animBackward1.setStartValue(end_pos)
        self.animBackward1.setEndValue(start_pos)
        if self.current_background == 0:
            self.background_label1.move(start_pos)
        
        # Background 2
        start_pos = QPoint(0, self.height() - self.pixmap2.height())
        end_pos = QPoint(self.width() - self.pixmap2.width(), 0)
        self.animForward2.setStartValue(start_pos)
        self.animForward2.setEndValue(end_pos)
        self.animBackward2.setStartValue(end_pos)
        self.animBackward2.setEndValue(start_pos)
        if self.current_background == 1:
            self.background_label2.move(start_pos)
        
        # Background 3
        start_pos = QPoint(0, self.height() - self.pixmap3.height())
        end_pos = QPoint(self.width() - self.pixmap3.width(), 0)
        self.animForward3.setStartValue(start_pos)
        self.animForward3.setEndValue(end_pos)
        self.animBackward3.setStartValue(end_pos)
        self.animBackward3.setEndValue(start_pos)
        if self.current_background == 2:
            self.background_label3.move(start_pos)
        
        # Background 4
        start_pos = QPoint(0, self.height() - self.pixmap4.height())
        end_pos = QPoint(self.width() - self.pixmap4.width(), 0)
        self.animForward4.setStartValue(start_pos)
        self.animForward4.setEndValue(end_pos)
        self.animBackward4.setStartValue(end_pos)
        self.animBackward4.setEndValue(start_pos)
        if self.current_background == 3:
            self.background_label4.move(start_pos)
        
        # Background 5
        start_pos = QPoint(0, self.height() - self.pixmap5.height())
        end_pos = QPoint(self.width() - self.pixmap5.width(), 0)
        self.animForward5.setStartValue(start_pos)
        self.animForward5.setEndValue(end_pos)
        self.animBackward5.setStartValue(end_pos)
        self.animBackward5.setEndValue(start_pos)
        if self.current_background == 4:
            self.background_label5.move(start_pos)
        
        # Background 6
        start_pos = QPoint(0, self.height() - self.pixmap6.height())
        end_pos = QPoint(self.width() - self.pixmap6.width(), 0)
        self.animForward6.setStartValue(start_pos)
        self.animForward6.setEndValue(end_pos)
        self.animBackward6.setStartValue(end_pos)
        self.animBackward6.setEndValue(start_pos)
        if self.current_background == 5:
            self.background_label6.move(start_pos)

    def update_time(self):
        current_time = QTime.currentTime()
        time_text = current_time.toString("hh:mm:ss")
        self.label_time.setText(time_text)

    def timer_button_click(self):
        self.timer_button_sound.play()
        original_geometry = self.timer_button.geometry()
        compressed_width = int(original_geometry.width() * 0.9)
        compressed_height = int(original_geometry.height() * 0.9)
        compressed_x = original_geometry.x() + (original_geometry.width() - compressed_width) // 2
        compressed_y = original_geometry.y() + (original_geometry.height() - compressed_height) // 2
        compressed_geometry = original_geometry.__class__(compressed_x, compressed_y, compressed_width, compressed_height)
        compress_anim = QPropertyAnimation(self.timer_button, b"geometry")
        compress_anim.setDuration(500)
        compress_anim.setStartValue(original_geometry)
        compress_anim.setEndValue(compressed_geometry)
        restore_anim = QPropertyAnimation(self.timer_button, b"geometry")
        restore_anim.setDuration(0)
        restore_anim.setStartValue(compressed_geometry)
        restore_anim.setEndValue(original_geometry)
        animation_group = QSequentialAnimationGroup(self)
        animation_group.addAnimation(compress_anim)
        animation_group.addAnimation(restore_anim)
        animation_group.finished.connect(self.timer_button_click_logic)
        animation_group.start()

    def timer_button_click_logic(self):
        if self.anim_group1.state() != QAbstractAnimation.State.Running:
            self.anim_group1.resume()
            self.anim_group2.resume()
            self.anim_group3.resume()
            self.anim_group4.resume()
            self.anim_group5.resume()
            self.anim_group6.resume()
            self.indicator.show()
        if self.timer_button.property("clicked") == 0 or self.timer_button.property("clicked") is None:
            self.timer_button.setProperty("clicked", 1)
            self.timer_button.setFlashValue(1.0)
            self.timer_label.show()
            self.cumulative_time_label.hide()
            self.cumulative_time_label.raise_()
            self.label_timer_background.show()
            self.task_input.show()
            self.bookmark_button.show()
            self.task_list.show()
            self.task_completed_button.hide()
            if not self.running:
                self.start_time = time.time()
            self.running = True
            self.timer_active = True
            self.timer_update_timer.start(100)
            self.fade_out_overlay(500)
        else:
            self.timer_button.setProperty("clicked", 0)
            self.timer_button.flash()
            self.timer_label.hide()
            self.cumulative_time_label.hide()
            self.label_timer_background.hide()
            self.task_input.hide()
            self.bookmark_button.hide()
            self.task_completed_button.hide()
            self.task_list.hide()
            self.running = False
            self.timer_active = False
            self.fade_in_overlay(500)
        self.update_timer_buttons_visibility()
        self.timer_button.hide()

    def pause_button_clicked(self):
        self.sound_effect.play()
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            self.running = False
            self.anim_group1.pause()
            self.anim_group2.pause()
            self.anim_group3.pause()
            self.anim_group4.pause()
            self.anim_group5.pause()
            self.anim_group6.pause()
            self.indicator.hide()
        self.update_timer_buttons_visibility()
        self.pause_button.setFlashValue(0.0)
        self.fade_in_overlay(500)

    def start_button_clicked(self):
        self.sound_effect.play()
        self.start_time = time.time() - self.elapsed_time
        self.running = True
        self.timer_update_timer.start(100)
        self.anim_group1.resume()
        self.anim_group2.resume()
        self.anim_group3.resume()
        self.anim_group4.resume()
        self.anim_group5.resume()
        self.anim_group6.resume()
        self.indicator.show()
        self.update_timer_buttons_visibility()
        self.fade_out_overlay(500)

    def timer_reset_button_clicked(self):
        self.sound_effect.play()
        self.pause_button.setFlashValue(0.0)
        self.running = False
        self.timer_update()
        self.elapsed_time = 0
        self.start_time = 0
        self.anim_group1.pause()
        self.anim_group2.pause()
        self.anim_group3.pause()
        self.anim_group4.pause()
        self.anim_group5.pause()
        self.anim_group6.pause()
        self.task_input.clear()
        self.indicator.hide()
        self.timer_active = False
        self.update_timer_buttons_visibility()
        self.update_all_button_icons()
        self.active_task_label.clear()
        self.active_task_label.hide()
        self.task_completed_button.hide()
        self.task_input.show()
        self.bookmark_button.show()
        self.timer_label.setText("00:00:00")
        self.cumulative_time_label.setText("00:00:00")
        self.fade_out_overlay(500)

    def timer_update(self):
        if self.running:
            self.elapsed_time = time.time() - self.start_time
        hours, rem = divmod(int(self.elapsed_time), 3600)
        minutes, seconds = divmod(rem, 60)
        self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")

    def update_timer_buttons_visibility(self):
        if self.timer_active and self.running:
            self.reset_button.show()
        else:
            self.reset_button.hide()
        if self.timer_active:
            if self.running:
                self.pause_button.show()
                self.start_button.hide()
            else:
                self.start_button.show()
                self.pause_button.hide()
        else:
            self.pause_button.hide()
            self.start_button.hide()

    def activate_task(self):
        self.sound_effect.play()
        if self.anim_group1.state() != QAbstractAnimation.State.Running:
            self.anim_group1.resume()
            self.anim_group2.resume()
            self.anim_group3.resume()
            self.anim_group4.resume()
            self.anim_group5.resume()
            self.anim_group6.resume()
        task_text = self.task_input.text().strip()
        if not task_text:
            return
        self.active_task_label.setText(task_text)
        self.active_task_label.setGeometry(self.task_input.geometry())
        shadow = QGraphicsDropShadowEffect(self.active_task_label)
        shadow.setBlurRadius(self.timer_label.shadow.blurRadius())
        shadow.setOffset(self.timer_label.shadow.offset())
        shadow.setColor(self.timer_label.shadow.color())
        self.active_task_label.setGraphicsEffect(shadow)
        start_pos = self.active_task_label.pos()
        start_pos.setX(-self.active_task_label.width())
        self.active_task_label.move(start_pos)
        self.active_task_label.show()
        animation = QPropertyAnimation(self.active_task_label, b"pos")
        animation.setDuration(500)
        animation.setStartValue(start_pos)
        final_pos = self.task_input.pos()
        animation.setEndValue(final_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.start()
        self.active_task_animation = animation
        self.task_input.hide()
        self.bookmark_button.hide()
        self.task_completed_button.show()
        if not self.running:
            self.start_time = time.time()
            self.running = True
            self.timer_active = True
            self.timer_update_timer.start(100)
        self.update_timer_buttons_visibility()
        self.fade_out_overlay(500)

    def add_task_to_list(self):
        self.anim_group1.pause()
        self.anim_group2.pause()
        self.anim_group3.pause()
        self.anim_group4.pause()
        self.anim_group5.pause()
        self.anim_group6.pause()
        self.sound_effect.play()
        task_text = self.active_task_label.text().strip()
        if not task_text:
            return
        time_text = self.timer_label.text()
        item_text = f"{time_text} - {task_text}"
        self.task_list.addItem(item_text)
        hh, mm, ss = map(int, time_text.split(':'))
        time_seconds = hh * 3600 + mm * 60 + ss
        self.total_time += time_seconds
        formatted_total = f"{self.total_time//3600:02d}:{(self.total_time % 3600)//60:02d}:{self.total_time%60:02d}"
        self.cumulative_time_label.setText("total time elapsed: " + formatted_total)
        self.active_task_label.clear()
        self.active_task_label.hide()
        self.task_completed_button.hide()
        self.task_input.show()
        self.task_input.clear()
        self.bookmark_button.show()
        self.running = False
        self.elapsed_time = 0
        self.start_time = 0
        self.timer_label.setText("00:00:00")
        self.cumulative_time_label.show()
        self.fade_in_overlay(500)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.startHoverAnimation(enter=True)

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.startHoverAnimation(enter=False)

    def startHoverAnimation(self, enter: bool):
        target_opacity = 1.0 if enter else 0.1
        target_blur = 2 if enter else 0
        for widget in [self.timer_label, self.cumulative_time_label, self.task_input, self.active_task_label]:
            anim_opacity = QPropertyAnimation(widget, b"textOpacity")
            anim_opacity.setDuration(3000)
            anim_opacity.setStartValue(widget.textOpacity)
            anim_opacity.setEndValue(target_opacity)
            anim_opacity.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            self.hover_animations.append(anim_opacity)
            shadow_effect = widget.graphicsEffect()
            if not shadow_effect:
                shadow_effect = QGraphicsDropShadowEffect(widget)
                shadow_effect.setBlurRadius(0)
                shadow_effect.setOffset(0)
                shadow_effect.setColor(QColor(255, 255, 255))
                widget.setGraphicsEffect(shadow_effect)
            anim_shadow = QPropertyAnimation(shadow_effect, b"blurRadius")
            anim_shadow.setDuration(3000)
            anim_shadow.setStartValue(shadow_effect.blurRadius())
            anim_shadow.setEndValue(target_blur)
            anim_shadow.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            self.hover_animations.append(anim_shadow)
            
        target_opacity_btn = 1.0 if enter else 0
        for btn in self.control_buttons:
            effect = btn.graphicsEffect()
            if effect is None:
                effect = QGraphicsOpacityEffect(btn)
                btn.setGraphicsEffect(effect)
            anim = QPropertyAnimation(effect, b"opacity")
            anim.setDuration(300)
            anim.setStartValue(effect.opacity())
            anim.setEndValue(target_opacity_btn)
            anim.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            self.hover_animations.append(anim)

    def showEvent(self, event):
        super().showEvent(event)
        self.setWindowOpacity(0)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(2000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        QTimer.singleShot(3000, lambda: self.fade_in_overlay(500))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Window()
    sound_effect = QSoundEffect()
    sound_effect.setSource(QUrl.fromLocalFile(resource_path("click.wav")))
    demo.show()
    sys.exit(app.exec())
