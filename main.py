from rich.console import Console


from my_xxt.my_tools import select_menu, show_start
from my_xxt.api import XcxyXxt
from my_xxt.login import login

console = Console(width=100)

if __name__ == '__main__':
    while True:
        show_start(console)
        xxt = XcxyXxt()
        login(console, xxt)
        select_menu(console, xxt)
