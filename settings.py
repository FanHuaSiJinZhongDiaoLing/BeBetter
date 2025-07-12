# settings.py

ALIAS_TO_EXE = {
    "qq": "QQ.exe",
}

CHECK_INTERVAL = 1         # 检测间隔，秒
TRIGGER_DURATION = 2         # 连续运行超过多少秒才弹窗
SUPPRESS_DURATION = 2       # 弹窗冷却时间，

# 快捷键（keyboard库格式）
HOTKEY = 'ctrl+alt+shift+q'

# 弹窗消息模板，支持{{name}}和{{time}}占位符
ALERT_MESSAGE_TEMPLATE = "你好像玩了{{time}}的{{name}}...休息一下吧？"
