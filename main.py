from rich.console import Console
from my_xxt.my_tools import select_menu, show_start
from my_xxt.api import NewXxt
from my_xxt.login import login

# 设置控制台的宽度
console = Console(width=120)

if __name__ == '__main__':
    while True:
        show_start(console)
        xxt = NewXxt()
        login(console, xxt)
        select_menu(console, xxt)
