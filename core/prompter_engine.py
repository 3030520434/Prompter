"""
提词器核心引擎 - 管理文本滚动逻辑
"""
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class PrompterEngine(QObject):
    """提词器引擎：控制文本滚动、速度、进度等"""

    # 信号定义
    position_changed = pyqtSignal(int)      # 当前位置变化 (行号)
    text_finished = pyqtSignal()            # 文本播放完成
    state_changed = pyqtSignal(str)         # 状态变化: playing/paused/stopped
    speed_changed = pyqtSignal(int)         # 速度变化

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text = ""
        self._lines = []
        self._current_line = 0
        self._total_lines = 0
        self._scroll_speed = 150  # 字/分钟
        self._is_playing = False
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._scroll_step)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value
        self._lines = value.split('\n') if value else []
        self._total_lines = len(self._lines)
        self._current_line = 0
        self._is_playing = False
        self._timer.stop()
        self.state_changed.emit("stopped")
        self.position_changed.emit(0)

    def update_total_lines(self, count: int):
        """更新总行数（视图换行后调用）"""
        self._total_lines = count

    @property
    def scroll_speed(self) -> int:
        return self._scroll_speed

    @scroll_speed.setter
    def scroll_speed(self, value: int):
        """设置滚动速度 (字/分钟)"""
        self._scroll_speed = max(20, min(500, value))
        if self._is_playing:
            self._update_timer_interval()
        self.speed_changed.emit(self._scroll_speed)

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def current_line(self) -> int:
        return self._current_line

    @property
    def total_lines(self) -> int:
        return self._total_lines

    @total_lines.setter
    def total_lines(self, value: int):
        """设置总行数（由视图更新换行后的行数）"""
        self._total_lines = value
        # 确保当前行不超过总行数
        if self._current_line >= self._total_lines:
            self._current_line = max(0, self._total_lines - 1)

    @property
    def total_chars(self) -> int:
        return len(self._text)

    @property
    def progress(self) -> float:
        """返回进度 0.0 - 1.0"""
        if self._total_lines == 0:
            return 0.0
        return self._current_line / self._total_lines

    def play(self):
        """开始/继续播放"""
        if self._total_lines == 0:
            return
        self._is_playing = True
        self._update_timer_interval()
        self._timer.start()
        self.state_changed.emit("playing")

    def pause(self):
        """暂停播放"""
        self._is_playing = False
        self._timer.stop()
        self.state_changed.emit("paused")

    def stop(self):
        """停止播放，回到开头"""
        self._is_playing = False
        self._timer.stop()
        self._current_line = 0
        self.state_changed.emit("stopped")
        self.position_changed.emit(0)

    def toggle_play_pause(self):
        """切换播放/暂停"""
        if self._is_playing:
            self.pause()
        else:
            self.play()

    def seek_to_line(self, line_number: int):
        """跳转到指定行"""
        self._current_line = max(0, min(line_number, self._total_lines - 1))
        self.position_changed.emit(self._current_line)

    def seek_to_progress(self, progress: float):
        """按进度跳转 0.0-1.0"""
        line = int(progress * self._total_lines)
        self.seek_to_line(line)

    def speed_up(self, step: int = 10):
        """加速"""
        self.scroll_speed = self._scroll_speed + step

    def speed_down(self, step: int = 10):
        """减速"""
        self.scroll_speed = self._scroll_speed - step

    def scroll_up(self, lines: int = 1):
        """向上滚动几行"""
        self.seek_to_line(self._current_line - lines)

    def scroll_down(self, lines: int = 1):
        """向下滚动几行"""
        self.seek_to_line(self._current_line + lines)

    def _update_timer_interval(self):
        """根据速度更新定时器间隔"""
        # 假设每行平均20个字，计算每行停留时间
        chars_per_line = 20
        chars_per_minute = self._scroll_speed
        ms_per_char = 60000 / chars_per_minute
        ms_per_line = int(ms_per_char * chars_per_line)
        self._timer.setInterval(max(50, ms_per_line))

    def _scroll_step(self):
        """滚动一步"""
        if self._current_line < self._total_lines - 1:
            self._current_line += 1
            self.position_changed.emit(self._current_line)
        else:
            # 播放完成
            self._is_playing = False
            self._timer.stop()
            self.state_changed.emit("stopped")
            self.text_finished.emit()
