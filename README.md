# 桌面提词器 (Desktop Prompter)

一个简洁实用的桌面提词器工具，支持单屏幕共享场景下的提词显示。

## 功能特性

- 📂 **文本导入** - 支持导入 .txt 文件
- 📝 **文本编辑** - 内置文本编辑器，实时修改
- ▶️ **播放控制** - 播放/暂停/停止/进度跳转
- 🎚️ **语速调节** - 20-500 字/分钟可调
- 🔤 **字体设置** - 字号、字体、行距可调
- �aggle **窗口置顶** - 始终显示在最上层，适合屏幕共享
- 🔄 **镜像翻转** - 支持水平翻转（配合硬件提词器）
- 🎨 **主题切换** - 黑底白字/黑底黄字/白底黑字
- ⌨️ **快捷键** - 键盘快捷操作，手部不离键盘

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Space` | 播放/暂停 |
| `↑` | 向上滚动一行 |
| `↓` | 向下滚动一行 |
| `+` `=` | 加速 |
| `-` | 减速 |
| `F11` | 全屏切换 |
| `Esc` | 退出全屏 |
| `Ctrl+O` | 打开文件 |
| `Ctrl+S` | 保存文件 |
| `Ctrl+E` | 编辑文本 |

## 安装与运行

### 环境要求
- Python 3.9+
- PyQt6

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行
```bash
python main.py
```

## 打包为 EXE

### 安装 PyInstaller
```bash
pip install pyinstaller
```

### 打包命令
```bash
pyinstaller build.spec
```

打包完成后，可执行文件位于 `dist/桌面提词器.exe`

### 单文件打包命令（备选）
```bash
pyinstaller --onefile --windowed --name="桌面提词器" main.py
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
│   ├── prompter_view.py     # 提词显示控件
│   └── settings_dialog.py   # 设置对话框（预留）
├── core/
│   ├── __init__.py
│   └── prompter_engine.py   # 提词引擎
└── resources/
    └── icons/
```

## 使用场景

1. **视频会议提词** - 窗口置顶，共享屏幕时不显示
2. **直播录屏** - 放置在屏幕边缘，方便阅读
3. **演讲排练** - 自由调节语速，适应不同需求

## 技术栈

- **Python 3.9+**
- **PyQt6** - GUI 框架
- **PyInstaller** - 打包工具

## 许可证

MIT License
