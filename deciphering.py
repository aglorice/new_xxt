# -*- coding = utf-8 -*-
# @Time :2023/3/12 18:35
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt
# @File :  deciphering.py

import execjs


def encrypto(phone, pwd):
    js_file = open('../../PycharmProjects/new_xxt/js/decrypt.js', 'r', encoding="utf-8").read()

    params = execjs.compile(js_file).call("encrypto", phone, pwd)
    return params
