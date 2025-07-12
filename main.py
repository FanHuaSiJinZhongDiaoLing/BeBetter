import sys
import os
import tkinter as tk
import psutil
import time
from threading import Thread
import keyboard
from collections import defaultdict
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import settings
from settings import *

class ProcessMonitorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.selected_aliases = set()
        self.running_start_time = {}
        self.last_alert_time = {}
        self.popup_lock = {}

        self.exe_to_aliases = defaultdict(list)
        for alias, exe in ALIAS_TO_EXE.items():
            self.exe_to_aliases[exe].append(alias)

        self.monitoring = True

    def launch_selector(self):
        selector = tk.Toplevel(self.root)
        selector.title("选择要监控的进程")
        selector.geometry("400x400")
        selector.configure(bg="#36393F")

        self.var_dict = {}
        frame = tk.Frame(selector, bg="#36393F")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        for alias, exe in ALIAS_TO_EXE.items():
            var = tk.IntVar()
            chk = tk.Checkbutton(frame, text=f"{alias} ({exe})", variable=var,
                                 font=("微软雅黑", 11), bg="#36393F", fg="#FFFFFF",
                                 selectcolor="#2C2F33", activebackground="#36393F", activeforeground="#FFFFFF")
            chk.pack(anchor='w', pady=3)
            self.var_dict[alias] = var

        def confirm():
            self.selected_aliases = {alias for alias, var in self.var_dict.items() if var.get() == 1}
            if not self.selected_aliases:
                tk.messagebox.showwarning("提示", "请至少选择一项！")
                return
            selector.destroy()
            self.setup_monitoring()
            self.start_hotkey_listener()

        tk.Button(selector, text="确定", command=confirm, bg="#7289DA", fg="#FFFFFF",
                  activebackground="#99AAB5", relief="flat", font=("微软雅黑", 11)).pack(pady=10)

        self.root.mainloop()

    def setup_monitoring(self):
        self.monitored_exes = set(ALIAS_TO_EXE[alias] for alias in self.selected_aliases)
        for exe in self.monitored_exes:
            self.running_start_time[exe] = None
            self.last_alert_time[exe] = 0
            self.popup_lock[exe] = False

    def get_running_process_names(self):
        return {proc.info['name'] for proc in psutil.process_iter(['name'])}

    def format_message(self, exe_name, alias_list, seconds):
        total_seconds = math.ceil(seconds)
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        parts = []
        if h > 0:
            parts.append(f"{h}小时")
        if m > 0:
            parts.append(f"{m}分钟")
        if s > 0 or not parts:
            parts.append(f"{s}秒")
        time_str = ''.join(parts)
        name = alias_list[0] if alias_list else exe_name
        msg = ALERT_MESSAGE_TEMPLATE.replace('{{name}}', name).replace('{{time}}', time_str)
        return msg

    def show_notification(self, exe_name, alias_list, run_seconds):
        if self.popup_lock[exe_name]:
            return
        self.popup_lock[exe_name] = True

        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)

        width, height = 360, 140
        x = (popup.winfo_screenwidth() - width) // 2
        y = (popup.winfo_screenheight() - height) // 2
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.configure(bg="#2C2F33")

        frame = tk.Frame(popup, bg="#2C2F33")
        frame.pack(expand=True, fill="both", padx=15, pady=15)

        msg = self.format_message(exe_name, alias_list, run_seconds)
        tk.Label(frame, text=msg, font=("微软雅黑", 12), fg="#FFFFFF", bg="#2C2F33", wraplength=320).pack(expand=True)

        def close_popup():
            popup.destroy()
            self.last_alert_time[exe_name] = time.time()
            self.popup_lock[exe_name] = False

        close_btn = tk.Button(frame, text="关闭", command=close_popup, bg="#7289DA", fg="#FFFFFF",
                              activebackground="#99AAB5", relief="flat", font=("微软雅黑", 10))
        close_btn.pack(pady=8)

        popup.after(5000, close_popup)

    def toggle_monitoring(self):
        self.monitoring = not self.monitoring
        print(f"监控已{'开启' if self.monitoring else '关闭'}")

    def start_hotkey_listener(self):
        keyboard.add_hotkey(HOTKEY, self.toggle_monitoring)
        Thread(target=self.monitor_loop, daemon=True).start()

    def monitor_loop(self):
        while True:
            if self.monitoring:
                running_exes = self.get_running_process_names()
                now = time.time()
                for exe in self.monitored_exes:
                    alias_list = self.exe_to_aliases[exe]
                    if exe in running_exes:
                        if self.running_start_time[exe] is None:
                            self.running_start_time[exe] = now
                        elif now - self.running_start_time[exe] >= TRIGGER_DURATION:
                            if (now - self.last_alert_time[exe] >= SUPPRESS_DURATION and
                                    not self.popup_lock[exe]):
                                run_time = now - self.running_start_time[exe]
                                self.root.after(0, self.show_notification, exe, alias_list, run_time)
                                self.running_start_time[exe] = None
                    else:
                        self.running_start_time[exe] = None
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    app = ProcessMonitorApp()
    app.launch_selector()
