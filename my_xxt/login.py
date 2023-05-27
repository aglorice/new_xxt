# -*- coding = utf-8 -*-
# @Time :2023/5/16 20:05
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  login.py
from rich.console import Console

from my_xxt.api import XcxyXxt


def login(console: Console, xxt: XcxyXxt) -> None:
    while True:
        phone = console.input("[yellow]请输入手机号:")
        password = console.input("[yellow]请输入密码:")
        login_status = xxt.login(phone, password)
        if not login_status["status"]:
            flag = console.input("[green]登录失败,请重新尝试！(按q退出,按任意键继续)")
            if flag == 'q':
                exit()
        else:
            info = xxt.getInfo()
            console.print(f"[green]登录成功,{info['name']}")
            break
