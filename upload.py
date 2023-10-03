import os
import re

from config import __VERSION__

"""
    修改README.md文件中的版本号
"""


def update_version():
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()
        content = re.sub(r"v\d+\.\d+\.\d+", f"{__VERSION__}", content)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(content)
    print("1.修改README.md文件中的版本号成功！")


"""
    提交新修改的README.md文件并推送到github
"""


def git_push_readme():
    os.system("git add .")
    os.system("git commit -m 'update version'")
    os.system("git push origin red")
    print("2.提交新修改的README.md文件并推送到github成功！")


"""
    自动生成创建新git tag标签，并上穿到github
"""


def git_tag():
    os.system("git tag -a v{} -m 'v{}'".format(__VERSION__, __VERSION__))
    os.system("git push origin v{}".format(__VERSION__))
    print("3.自动生成创建新git tag标签，并上穿到github成功！")


if __name__ == '__main__':
    update_version()
    git_push_readme()
    git_tag()
