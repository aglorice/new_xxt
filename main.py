from rich.console import Console
from rich.traceback import install

from my_xxt.my_tools import select_menu, show_start
from my_xxt.api import NewXxt
from my_xxt.login import login
from config import __LOG_FILE__, __SCREEN_WIDTH__


class MyConsole(Console):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_file = open(__LOG_FILE__, "w", encoding="utf-8")

    def log(self, *args, **kwargs):
        super().log(*args, **kwargs)
        if not self.log_file.closed:
            self.log_file.write("\n"+" ".join(map(str, args)) + "\n")

    def print(self, *args, **kwargs):
        super().print(*args, **kwargs)
        captured_output_value = super().export_text()
        if not self.log_file.closed:
            self.log_file.write("\n"+captured_output_value+"\n")

    def cleanup(self):
        if not self.log_file.closed:
            self.log_file.close()

    def __del__(self):
        self.cleanup()


def main():
    console = MyConsole(width=__SCREEN_WIDTH__, record=True)
    install(console=console, show_locals=True, width=__SCREEN_WIDTH__)

    try:
        while True:
            show_start(console)
            new_xxt_instance = NewXxt()
            login(console, new_xxt_instance)
            select_menu(console, new_xxt_instance)
    except Exception as e:
        console.log(f"程序退出: {e}", style="bold red")
        console.log_exception(e)
        console.log("如果需要反馈错误信息，请将对应的日志文件以及问题反映给作者", style="bold red")


if __name__ == '__main__':
    main()
