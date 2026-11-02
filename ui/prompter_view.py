"""
提词器显示控件 - 文字不断向上滚动，像真正的提词器一样
支持根据窗口宽度自动换行，平滑像素级滚动
"""
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QFont, QColor, QPen, QFontMetrics
from PyQt6.QtWidgets import QWidget


class PrompterView(QWidget):
    """提词器显示控件 - 文字不断向上滚动"""

    clicked = pyqtSignal()
    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
        self._scroll_y = 0.0  # 滚动位置（浮点数，像素级）
        self._font_size = 28
        self._font_family = "Microsoft YaHei"
        self._text_color = QColor(255, 255, 255)
        self._bg_color = QColor(0, 0, 0)
        self._highlight_color = QColor(255, 255, 0)
        self._line_spacing = 1.5
        self._padding = 30
        self._is_playing = False
        self._scroll_speed = 40  # 字/分钟
        self._scroll_timer = QTimer(self)
        self._scroll_timer.timeout.connect(self._scroll_step)
        self._lines = []  # 换行后的行

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), self._bg_color)
        self.setPalette(palette)

    def set_font_size(self, size: int):
        self._font_size = max(12, min(72, size))
        self._rewrap_text()
        self.update()

    def set_text_color(self, color: QColor):
        self._text_color = color
        self.update()

    def set_background_color(self, color: QColor):
        self._bg_color = color
        palette = self.palette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)
        self.update()

    def set_highlight_color(self, color: QColor):
        self._highlight_color = color
        self.update()

    def set_line_spacing(self, spacing: float):
        self._line_spacing = max(1.0, min(3.0, spacing))
        self._rewrap_text()
        self.update()

    def set_text(self, text: str):
        """设置文本"""
        self._text = text
        self._scroll_y = 0.0
        self._rewrap_text()
        self.update()

    def set_scroll_speed(self, speed: int):
        """设置滚动速度"""
        self._scroll_speed = max(10, min(80, speed))

    def play(self):
        """开始滚动"""
        if self._text:
            self._is_playing = True
            self._scroll_timer.start(16)  # 约60fps

    def pause(self):
        """暂停滚动"""
        self._is_playing = False
        self._scroll_timer.stop()

    def stop(self):
        """停止滚动，停在当前位置"""
        self._is_playing = False
        self._scroll_timer.stop()
        self.update()

    def toggle_play_pause(self):
        if self._is_playing:
            self.pause()
        else:
            self.play()

    def speed_up(self, step=10):
        self.set_scroll_speed(self._scroll_speed + step)

    def speed_down(self, step=10):
        self.set_scroll_speed(self._scroll_speed - step)

    def scroll_up(self):
        self._scroll_y = max(0, self._scroll_y - 30)
        self.update()

    def scroll_down(self):
        self._scroll_y += 30
        self.update()

    @property
    def font_size(self):
        return self._font_size

    @property
    def total_chars(self):
        return len(self._text)

    @property
    def _is_playing_state(self):
        return self._is_playing

    def _rewrap_text(self):
        """根据窗口宽度自动换行"""
        if not self._text:
            self._lines = []
            return

        font = QFont(self._font_family, self._font_size)
        metrics = QFontMetrics(font)
        available_width = self.width() - self._padding * 2
        if available_width < 50:
            available_width = 50

        self._lines = []
        for paragraph in self._text.split('\n'):
            if not paragraph:
                self._lines.append('')
            else:
                self._lines.extend(self._split_line(paragraph, available_width, metrics))

    def _split_line(self, text, max_width, metrics):
        """按宽度分割一行"""
        lines = []
        i = 0
        while i < len(text):
            end = self._find_break(i, text, max_width, metrics)
            segment = text[i:end].rstrip()
            lines.append(segment)
            i = end
        return lines

    def _find_break(self, start, line, max_width, metrics):
        """找到最佳断行位置"""
        if metrics.horizontalAdvance(line[start:]) <= max_width:
            return len(line)

        # 二分查找
        low, high = 1, len(line) - start
        best = 1
        while low <= high:
            mid = (low + high) // 2
            if metrics.horizontalAdvance(line[start:start + mid]) <= max_width:
                best = mid
                low = mid + 1
            else:
                high = mid - 1

        # 在标点处断行
        end = start + best
        if end < len(line):
            for j in range(end - 1, max(start, end - best // 2), -1):
                if line[j] in '，。！？；：、 ）】」』)] ' :
                    return j + 1
        return end

    def _scroll_step(self):
        """每帧滚动 - 向上移动像素"""
        # 根据速度计算每帧移动的像素数
        # 速度是字/分钟，假设每行约20字，每行高度约 font_size * line_spacing
        font = QFont(self._font_family, self._font_size)
        metrics = QFontMetrics(font)
        line_height = metrics.height() * self._line_spacing
        chars_per_line = max(1, (self.width() - self._padding * 2) // max(1, metrics.horizontalAdvance('中')))

        # 每秒移动的像素
        pixels_per_second = (self._scroll_speed / 60) * chars_per_line * line_height / 20
        # 每帧移动的像素 (16ms一帧)
        pixels_per_frame = pixels_per_second * 0.016

        self._scroll_y += max(0.5, pixels_per_frame)
        self.update()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self._scroll_y = max(0, self._scroll_y - 40)
        else:
            self._scroll_y += 40
        self.update()
        super().wheelEvent(event)

    def resizeEvent(self, event):
        """窗口大小变化时重新换行"""
        self._rewrap_text()
        super().resizeEvent(event)

    def paintEvent(self, event):
        """绘制 - 文字不断向上滚动"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

        # 背景
        painter.fillRect(self.rect(), self._bg_color)

        if not self._lines:
            painter.setPen(QColor(150, 150, 150))
            font = QFont(self._font_family, 16)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "请导入或输入提词文本")
            return

        # 字体
        font = QFont(self._font_family, self._font_size)
        painter.setFont(font)
        metrics = QFontMetrics(font)
        line_height = int(metrics.height() * self._line_spacing)

        # 中心Y坐标（阅读线位置）
        center_y = self.height() // 2

        # 绘制每一行
        for i, line in enumerate(self._lines):
            # 计算每行的Y坐标：从下方远处向上移动
            y_f = center_y + (i * line_height) - self._scroll_y + metrics.ascent()
            y = int(y_f)

            # 只绘制可见区域
            if y < -line_height or y > self.height() + line_height:
                continue

            # 判断是否是当前行（最接近中心）
            line_center = y - metrics.ascent() + line_height // 2
            dist_to_center = abs(line_center - center_y)
            is_current = dist_to_center < line_height // 2

            if is_current:
                painter.setPen(self._highlight_color)
                hy = y - metrics.ascent()
                highlight_rect = (self._padding - 5, hy - 5,
                                  self.width() - self._padding * 2 + 10, line_height)
                painter.fillRect(*highlight_rect, QColor(50, 50, 50, 100))
            else:
                painter.setPen(self._text_color)

            painter.drawText(self._padding, y, line)

        # 中心阅读线
        pen = QPen(QColor(255, 0, 0, 180), 2, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(0, center_y, self.width(), center_y)

        # 顶部和底部渐变遮罩（让文字淡入淡出）
        gradient_top = self.rect().adjusted(0, 0, 0, -self.height() * 7 // 10)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillRect(gradient_top, QColor(0, 0, 0, 0))

        painter.end()
