# 桌面提词器 (Desktop Prompter)

一个简洁实用的 Windows 桌面提词器工具，支持单屏幕共享场景下的提词显示。

## 下载

直接从 [Releases](https://github.com/3030520434/Prompter/releases) 下载最新版 `DesktopPrompter.exe`，无需安装，双击即可使用。

## 功能特性

- 📂 **文本导入** - 支持导入 .txt 文件，自动适应窗口换行
- 📝 **文本编辑** - 内置文本编辑器，实时修改
- ▶️ **播放控制** - 播放 / 暂停 / 停止（停止不回归顶部）
- 🎚️ **语速调节** - 5 ~ 80 字/分钟可调，预设慢速 20 / 正常 40 / 快速 60
- 🔤 **字体设置** - 字号 12-72、字体、行距可调（默认字号 20）
- 📌 **窗口置顶** - 始终显示在最上层
- 🔒 **防截屏** - 屏幕共享时隐藏窗口内容（Anti-Capture）
- 🪟 **小窗模式** - Ctrl+M 切换小窗，带标题栏可拖拽调整大小
- ⌨️ **快捷键** - 键盘快捷操作，解放鼠标

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Space` | 播放 / 暂停 |
| `↑` | 向上滚动一行 |
| `↓` | 向下滚动一行 |
| `+` `=` | 加速（步进 5） |
| `-` `_` | 减速（步进 5） |
| `F11` | 全屏切换 |
| `Esc` | 退出全屏 |
| `Ctrl+M` | 切换小窗模式 |
| `Ctrl+O` | 打开文件 |
| `Ctrl+S` | 保存文件 |
| `Ctrl+E` | 编辑文本 |

## 使用场景

1. **视频会议提词** - 窗口置顶 + 防截屏，共享屏幕时不暴露提词内容
2. **直播录屏** - 小窗模式放置在屏幕边缘，方便阅读
3. **演讲排练** - 自由调节语速，适应不同节奏

## 开发者：本地运行与打包

### 环境要求
- Python 3.9+
- PyQt6

### 安装依赖并运行
```bash
pip install -r requirements.txt
python main.py
```

### 打包为 EXE
```bash
pip install pyinstaller
pyinstaller build.spec
```

## 项目结构

```
Prompter/
├── main.py                  # 程序入口
├── requirements.txt         # Python 依赖
├── build.spec               # PyInstaller 打包配置
├── README.md                # 使用说明
├── ui/
│   ├── __init__.py
│   ├── main_window.py       # 主窗口
│   └── prompter_view.py     # 提词显示控件
├── core/
│   ├── __init__.py
│   └── prompter_engine.py   # 提词引擎
└── resources/
    └── icons/
```

## 技术栈

- **Python 3.9+**
- **PyQt6** - GUI 框架
- **PyInstaller** - 打包工具

## 许可证

MIT License
