"""
主窗口界面 - 桌面提词器 v1.0
"""
import sys
import os
import ctypes
from ctypes import wintypes

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QAction, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QSlider, QLabel, QFileDialog, QMessageBox,
    QFrame, QMenuBar, QToolBar, QStatusBar,
    QSpinBox, QDoubleSpinBox, QGroupBox,
    QApplication
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.prompter_view import PrompterView

# Windows API for anti-capture
user32 = ctypes.windll.user32
WDA_NONE = 0x00000000
WDA_MONITOR = 0x00000001
WDA_EXCLUDEFROMCAPTURE = 0x00000011  # Windows 10 1903+


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("桌面提词器 v1.0")
        self.setMinimumSize(300, 200)
        self.resize(800, 500)

        self._setup_ui()
        self._setup_menu()
        self._setup_shortcuts()

        # 窗口置顶
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self._load_demo_text()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 提词器显示
        self.prompter = PrompterView()
        self.prompter.clicked.connect(self._toggle_play)
        self.prompter.double_clicked.connect(self._exit_mini_mode)
        layout.addWidget(self.prompter, 1)

        # 控制面板
        self.control_panel = self._create_control_panel()
        layout.addWidget(self.control_panel)

        # 小窗退出按钮
        self.btn_mini_exit = QPushButton("✕", self)
        self.btn_mini_exit.setFixedSize(24, 24)
        self.btn_mini_exit.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 180);
                color: white; border: none; border-radius: 12px;
                font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(255, 0, 0, 255); }
        """)
        self.btn_mini_exit.clicked.connect(self._toggle_mini_mode)
        self.btn_mini_exit.hide()

    def _create_control_panel(self):
        panel = QFrame()
        panel.setMaximumHeight(130)
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(10, 5, 10, 5)

        # 播放控制
        btn_group = QGroupBox("播放控制")
        btn_layout = QHBoxLayout(btn_group)

        self.btn_play = QPushButton("\u25B6 播放")
        self.btn_play.setMinimumWidth(80)
        self.btn_play.clicked.connect(self._toggle_play)
        btn_layout.addWidget(self.btn_play)

        self.btn_stop = QPushButton("\u25FC 停止")
        self.btn_stop.setMinimumWidth(80)
        self.btn_stop.clicked.connect(self._stop)
        btn_layout.addWidget(self.btn_stop)
        layout.addWidget(btn_group)

        # 速度控制
        speed_group = QGroupBox("语速控制")
        speed_layout = QVBoxLayout(speed_group)

        speed_top = QHBoxLayout()
        self.lbl_speed = QLabel("40 字/分钟")
        speed_top.addWidget(self.lbl_speed)
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(10, 80)
        self.slider_speed.setValue(40)
        self.slider_speed.valueChanged.connect(self._on_speed_changed)
        speed_top.addWidget(self.slider_speed, 1)
        speed_layout.addLayout(speed_top)

        presets = QHBoxLayout()
        for speed, label in [(20, "慢速"), (40, "正常"), (60, "快速")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=speed: self._set_speed(s))
            presets.addWidget(btn)
        speed_layout.addLayout(presets)
        layout.addWidget(speed_group, 1)

        # 字体设置
        font_group = QGroupBox("字体设置")
        font_layout = QHBoxLayout(font_group)
        font_layout.addWidget(QLabel("字号:"))
        self.spin_font = QSpinBox()
        self.spin_font.setRange(12, 72)
        self.spin_font.setValue(28)
        self.spin_font.valueChanged.connect(self._on_font_changed)
        font_layout.addWidget(self.spin_font)
        font_layout.addWidget(QLabel("行距:"))
        self.spin_spacing = QDoubleSpinBox()
        self.spin_spacing.setRange(1.0, 3.0)
        self.spin_spacing.setSingleStep(0.1)
        self.spin_spacing.setValue(1.5)
        self.spin_spacing.valueChanged.connect(self._on_spacing_changed)
        font_layout.addWidget(self.spin_spacing)
        layout.addWidget(font_group)

        return panel

    def _setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件(&F)")
        
        action_open = QAction("打开(&O)...", self)
        action_open.setShortcut(QKeySequence.StandardKey.Open)
        action_open.triggered.connect(self._open_file)
        file_menu.addAction(action_open)
        
        action_save = QAction("保存(&S)...", self)
        action_save.setShortcut(QKeySequence.StandardKey.Save)
        action_save.triggered.connect(self._save_file)
        file_menu.addAction(action_save)
        
        file_menu.addSeparator()
        action_quit = QAction("退出(&X)", self)
        action_quit.setShortcut(QKeySequence.StandardKey.Quit)
        action_quit.triggered.connect(self.close)
        file_menu.addAction(action_quit)

        view_menu = menubar.addMenu("视图(&V)")
        
        action_fullscreen = QAction("全屏(&F)", self)
        action_fullscreen.setShortcut("F11")
        action_fullscreen.triggered.connect(self._toggle_fullscreen)
        view_menu.addAction(action_fullscreen)
        
        action_mini = QAction("小窗模式(&M)", self)
        action_mini.setShortcut("Ctrl+M")
        action_mini.triggered.connect(self._toggle_mini_mode)
        view_menu.addAction(action_mini)
        self.action_top = QAction("窗口置顶(&T)", self)
        self.action_top.setCheckable(True)
        self.action_top.setChecked(True)
        self.action_top.triggered.connect(self._toggle_top)
        view_menu.addAction(self.action_top)
        
        # 防偷屏选项
        self.action_anti_capture = QAction("防偷屏(&A)", self)
        self.action_anti_capture.setCheckable(True)
        self.action_anti_capture.setChecked(False)
        self.action_anti_capture.triggered.connect(self._toggle_anti_capture)
        self.action_anti_capture.setToolTip("开启后，屏幕共享/录屏软件无法捕获此窗口")
        view_menu.addAction(self.action_anti_capture)
        
        view_menu.addSeparator()
        theme_menu = view_menu.addMenu("主题(&H)")
        theme_menu.addAction("黑底白字", lambda: self._set_theme("black"))
        theme_menu.addAction("黑底黄字", lambda: self._set_theme("yellow"))
        theme_menu.addAction("白底黑字", lambda: self._set_theme("white"))

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Space"), self, self._toggle_play)
        QShortcut(QKeySequence("Up"), self, lambda: self.prompter.scroll_up())
        QShortcut(QKeySequence("Down"), self, lambda: self.prompter.scroll_down())
        QShortcut(QKeySequence("+"), self, self._speed_up)
        QShortcut(QKeySequence("-"), self, self._speed_down)
        QShortcut(QKeySequence("="), self, self._speed_up)
        QShortcut(QKeySequence("_"), self, self._speed_down)
        QShortcut(QKeySequence("Escape"), self, self._exit_fullscreen)

    def _load_demo_text(self):
        text = "欢迎使用桌面提词器\n\n这是一个简洁实用的桌面提词器工具，专为单屏幕共享场景设计。\n\n主要功能：\n1. 支持导入文本文件，自动适应窗口宽度换行\n2. 支持语速调节（20-500字/分钟）\n3. 支持字体大小、行距调节\n4. 支持窗口置顶，共享屏幕时不被遮挡\n5. 支持小窗模式，只显示滚动区域\n\n快捷键说明：\n- 空格键：播放/暂停\n- 上下箭头：手动滚动\n- +/-：加速/减速\n- F11：全屏切换\n- Ctrl+M：小窗模式切换\n- Ctrl+O：打开文件\n- Ctrl+E：编辑文本\n\n使用说明：\n1. 点击打开按钮导入文本文件，或点击编辑按钮直接输入文本\n2. 点击播放按钮开始滚动，文本会自动适应窗口宽度\n3. 使用滑块调节滚动速度\n4. 按Ctrl+M切换到小窗模式\n\n文本会根据窗口大小自动换行，您可以自由调整窗口大小。\n\n祝您使用愉快！"
        self.prompter.set_text(text)

    def _toggle_play(self):
        self.prompter.toggle_play_pause()
        if self.prompter._is_playing_state:
            self.btn_play.setText("\u23F8 暂停")
        else:
            self.btn_play.setText("\u25B6 播放")

    def _stop(self):
        self.prompter.stop()
        self.btn_play.setText("\u25B6 播放")

    def _on_speed_changed(self, value):
        self.prompter.set_scroll_speed(value)
        self.lbl_speed.setText(f"{value} 字/分钟")

    def _set_speed(self, speed):
        self.slider_speed.setValue(speed)

    def _on_font_changed(self, size):
        self.prompter.set_font_size(size)

    def _on_spacing_changed(self, spacing):
        self.prompter.set_line_spacing(spacing)

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "打开文本文件", "", "文本文件 (*.txt);;所有文件 (*)")
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.prompter.set_text(text)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法打开文件:\n{e}")

    def _save_file(self):
        path, _ = QFileDialog.getSaveFileName(self, "保存文本文件", "", "文本文件 (*.txt)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.prompter._text)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法保存文件:\n{e}")

    def _edit_text(self):
        from PyQt6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑文本")
        dialog.setMinimumSize(500, 400)
        layout = QVBoxLayout(dialog)
        edit = QTextEdit()
        edit.setPlainText(self.prompter._text)
        layout.addWidget(edit)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.prompter.set_text(edit.toPlainText())

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _exit_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()

    def _toggle_mini_mode(self):
        if self.control_panel.isVisible():
            self._mini_mode = True
            self.control_panel.hide()
            self.menuBar().hide()
            # 无边框窗口，只显示滚动区域
            self.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.FramelessWindowHint
            )
            self.show()
            self.resize(self.width(), 120)
            self.btn_mini_exit.move(self.width() - 30, 6)
            self.btn_mini_exit.show()
            self.btn_mini_exit.raise_()
        else:
            self._mini_mode = False
            self.control_panel.show()
            self.menuBar().show()
            # 恢复有边框窗口
            self.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint
            )
            self.show()
            self.resize(self.width(), 500)
            self.btn_mini_exit.hide()

    def _exit_mini_mode(self):
        if not self.control_panel.isVisible():
            self._toggle_mini_mode()

    def _toggle_top(self, checked):
        flags = self.windowFlags()
        if checked:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def _toggle_anti_capture(self, checked):
        """开启/关闭防偷屏 - 屏幕共享时窗口不可见"""
        try:
            hwnd = int(self.winId())
            if checked:
                # WDA_EXCLUDEFROMCAPTURE - 从屏幕捕获中排除（Win10 1903+）
                # 如果不支持则回退到 WDA_MONITOR
                result = user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)
                if not result:
                    # 回退到 WDA_MONITOR
                    user32.SetWindowDisplayAffinity(hwnd, WDA_MONITOR)
            else:
                user32.SetWindowDisplayAffinity(hwnd, WDA_NONE)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"设置防偷屏失败:\n{e}")

    def _set_theme(self, name):
        themes = {
            "black": (QColor(0, 0, 0), QColor(255, 255, 255), QColor(255, 255, 0)),
            "yellow": (QColor(0, 0, 0), QColor(255, 255, 0), QColor(255, 255, 255)),
            "white": (QColor(255, 255, 255), QColor(0, 0, 0), QColor(255, 0, 0)),
        }
        bg, text, hl = themes[name]
        self.prompter.set_background_color(bg)
        self.prompter.set_text_color(text)
        self.prompter.set_highlight_color(hl)

    def _speed_up(self):
        self.prompter.speed_up()
        self.slider_speed.setValue(self.prompter._scroll_speed)

    def _speed_down(self):
        self.prompter.speed_down()
        self.slider_speed.setValue(self.prompter._scroll_speed)

    def resizeEvent(self, event):
        # 更新小窗退出按钮位置
        if hasattr(self, 'btn_mini_exit') and self.btn_mini_exit.isVisible():
            self.btn_mini_exit.move(self.width() - 30, 6)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        # 无边框小窗模式下，支持拖动窗口
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.control_panel.isVisible():
                self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not self.control_panel.isVisible() and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
        super().mouseMoveEvent(event)

    def closeEvent(self, event):
        self.prompter.stop()
        super().closeEvent(event)
