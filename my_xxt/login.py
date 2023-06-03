# -*- coding = utf-8 -*-
# @Time :2023/5/16 20:05
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  login.py
import time

from qrcode import QRCode
from rich.console import Console

from my_xxt.api import XcxyXxt
from my_xxt.my_tools import select_error


def login(console: Console, xxt: XcxyXxt) -> None:
    while True:
        choose = select_login(console)
        if choose == "1":
            ret = phone_login(console, xxt)
            if ret:
                break
        elif choose == "2":
            ret = qr_login(console, xxt)
            if ret:
                break
        else:
            select_error(console)


def select_login(console: Console):
    console.rule("登录方式")
    console.print("1.手机号密码登录")
    console.print("2.扫码登录")
    console.rule("")
    choose = console.input("请选择你要登录的方式:")
    return choose


def phone_login(console: Console, xxt: XcxyXxt):
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
            return True


def qr_login(console: Console, xxt: XcxyXxt):
    xxt.qr_get()
    qr = QRCode()
    qr.add_data(xxt.qr_geturl())
    qr.print_ascii(invert=True)
    console.log("[yellow]等待扫描")
    flag_scan = False
    while True:
        qr_status = xxt.login_qr()
        if qr_status["status"]:
            info = xxt.getInfo()
            console.print(f"[green]登录成功,{info['name']}")
            return True
        match qr_status.get("type"):
            case "1":
                console.print("[red]二维码验证错误")
                break
            case "2":
                console.print("[red]二维码已失效")
                break
            case "4":
                if not flag_scan:
                    console.print(
                        f"[green]二维码已扫描"
                    )
                flag_scan = True
        time.sleep(1.0)
