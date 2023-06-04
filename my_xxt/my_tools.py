# -*- coding = utf-8 -*-
# @Time :2023/5/16 18:36
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  my_tools.py
import difflib
import json
import os
import shutil
import time

from rich.console import Console
from rich.table import Table

from my_xxt.findAnswer import match_answer
from my_xxt.api import NewXxt


def select_error(console: Console):
    console.print("[green]发生了一些未知的错误！")
    flag = console.input("[green]请选择是否重新选择！(按q退出,按任意键继续)")
    if flag == 'q':
        exit(0)


def select_course(console: Console, courses: list) -> dict:
    while True:
        index = console.input("[yellow]请输入你要打开的课程的序号：")
        for item in courses:
            if item["id"] == index:
                return item
        select_error(console)


def select_work(console: Console, works: list) -> dict:
    if not len(works):
        return {}
    while True:
        index = console.input("[yellow]请输入作业答案的id：")
        for item in works:
            if item["work_id"] == index:
                return item
        select_error(console)


def select_menu(console: Console, xxt: NewXxt) -> None:
    while True:
        show_menu(console)
        index = console.input("[yellow]请输入你想选择的功能：")
        # 查看课程
        if index == "1":
            courses = xxt.getCourse()
            show_course(courses, console)
            continue
        # 查看所有的答案文件
        elif index == "2":
            show_all_answer_file(console)
            continue
        # 查看左右为完成的作业
        elif index == "3":
            courses = xxt.getCourse()
            not_work = get_not_work(courses, xxt, console, sleep_time=2)
            show_not_work(not_work, console)
            continue
        # 清除所有的答案文件
        elif index == "4":
            dirpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            path = os.path.join(dirpath, "answers")
            del_file(path)
            console.print(f"[green]清空完毕")
            continue
        # 爬取指定课程的指定的作业（已完成）
        elif index == "5":
            courses = xxt.getCourse()
            show_course(courses, console)
            course = select_course(console, courses)
            works = xxt.getWorks(course["course_url"], course["course_name"])
            show_works(works, console)

            # 爬取答案
            work = select_work(console, works)
            if work == {}:
                console.print("[red]该课程下没有作业")
                continue
            if work["work_status"] == "已完成":
                answer_list = xxt.getAnswer(work["work_url"])
            else:
                console.print("[red]该作业似乎没有完成")
                continue
            # 保存答案至answer文件
            dateToJsonFile(answer_list, work)
            console.print(f"[green]爬取成功，答案已经保存至{work['id']}.json")
            continue
        # 完成指定课程的指定作业（未完成）
        elif index == "6":
            courses = xxt.getCourse()
            show_course(courses, console)
            course = select_course(console, courses)
            works = xxt.getWorks(course["course_url"], course["course_name"])
            show_works(works, console)

            # 完成作业
            work = select_work(console, works)
            if work == {}:
                console.print("[red]该课程下没有作业")
                continue
            if work["work_status"] == "已完成":
                console.print("[red]该作业已经完成了")
                continue
            else:
                questions = xxt.get_question(work["work_url"])
            if not is_exist_answer_file(f"{work['id']}.json"):
                console.print("[green]没有在答案文件中匹配到对应的答案文件")
                continue
            else:
                dirpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                path = os.path.join(dirpath, "answers", f"{work['id']}.json")
                answer = match_answer(jsonFileToDate(path)[work["id"]], questions)
                show_answer(answer_list=answer, console=console)
            choose = console.input("[yellow]是否继续进行提交：（yes/no）")
            if not (choose == "yes"):
                continue
            ret = xxt.commit_work(answer, work)
            console.print(ret)
            works = xxt.getWorks(course["course_url"], course["course_name"])
            show_works(works, console)
            continue
        # 退出登录
        elif index == "7":
            return
        select_error(console)


def show_start(console: Console) -> None:
    console.rule("欢迎使用该做题脚本")
    console.print("    ███╗   ██╗███████╗██╗    ██╗        ██╗  ██╗██╗  ██╗████████╗\n \
   ████╗  ██║██╔════╝██║    ██║        ╚██╗██╔╝╚██╗██╔╝╚══██╔══╝\n \
 ██╔██╗ ██║█████╗  ██║ █╗ ██║         ╚███╔╝  ╚███╔╝    ██║\n\
  ██║╚██╗██║██╔══╝  ██║███╗██║         ██╔██╗  ██╔██╗    ██║\n\
  ██║ ╚████║███████╗╚███╔███╔╝███████╗██╔╝ ██╗██╔╝ ██╗   ██║\n\
  ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝  ", justify="center")

    console.print("[red]注意：该脚本仅供学习参考,详细信息请参考https://github.com/aglorice/new_xxt")


def show_course(courses: list, console: Console) -> None:
    tb = Table("序号", "课程名", "老师名", border_style="blue")
    for course in courses:
        tb.add_row(
            f"[green]{course['id']}",
            course["course_name"],
            course["course_teacher"],
        )
    console.rule("[blue]课程信息", characters="*")
    console.print(tb)


def show_menu(console: Console) -> None:
    console.rule("[green]菜单", characters="+")
    console.print("1.查看课程", highlight=True)
    console.print("2.查看当前所有答案文件", highlight=True)
    console.print("3.查询所有未完成的作业", highlight=True)
    console.print("4.清除所有答案文件", highlight=True)
    console.print("5.爬取指定作业的答案", highlight=True)
    console.print("6.完成作业（请先确认是否已经爬取了你想要完成作业的答案）", highlight=True)
    console.print("7.退出登录", highlight=True)
    console.rule(characters="+")


def show_works(works: list, console: Console) -> None:
    tb = Table("id", "作业名称", "作业状态", "分数", "是否可以重做", border_style="blue")
    for work in works:
        tb.add_row(
            f"[green]{work['work_id']}",
            work['work_name'],
            work["work_status"],
            work["score"],
            work["isRedo"]
        )
    console.rule("[blue]作业信息", characters="*")
    console.print(tb)


def show_answer(console: Console, answer_list: list) -> None:
    tb = Table("id", "题目名称", "答案", border_style="blue")
    for answer in answer_list:
        tb.add_row(
            f"[green]{answer['id']}",
            answer['title'],
            str(answer["answer"])
        )
    console.rule("[blue]检查答案", characters="*")
    console.print(tb)


def dateToJsonFile(answer: list, info: dict) -> None:
    """
    将答案写入文件保存为json格式
    :param answer:
    :param info:
    :return:
    """
    to_dict = {
        info["id"]: answer,
        "info": info
    }
    # json.dumps 序列化时对中文默认使用的ascii编码.想输出真正的中文需要指定ensure_ascii=False
    json_data = json.dumps(to_dict, ensure_ascii=False)
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path = os.path.join(path, "answers", f"{info['id']}.json")
    with open(path, 'w', encoding="utf-8") as f_:
        f_.write(json_data)


def jsonFileToDate(file: str) -> dict:
    with open(file, 'r', encoding="utf-8") as f_:
        json_data = dict(json.loads(f_.read()))
    return json_data


def show_all_answer_file(console: Console) -> None:
    answer_files = []
    answer_file_info = []
    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path = os.path.join(dir_path, "answers")
    for root, dirs, files in os.walk(path):
        answer_files.append(files)
    for item in answer_files[0]:
        _path = path + '\\' + item
        answer_file_info.append(jsonFileToDate(_path)["info"])

    tb = Table("id", "作业名", "文件名称", "课程名称", border_style="blue")
    for work_info in answer_file_info:
        tb.add_row(
            f"[green]{work_info['id']}",
            work_info["work_name"],
            work_info["id"] + ".json",
            work_info["course_name"],
        )
    console.rule("[blue]作业文件列表", characters="*")
    console.print(tb)


def is_exist_answer_file(work_file_name: str) -> bool:
    answer_files = []
    dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path = os.path.join(dir_path, "answers")
    for root, dirs, files in os.walk(path):
        answer_files.append(files)
    if work_file_name in answer_files[0]:
        return True
    else:
        return False


def del_file(path_data: str):
    for i in os.listdir(path_data):  # os.listdir(path_data)#返回一个列表，里面是当前目录下面的所有东西的相对路径
        file_data = path_data + "\\" + i  # 当前文件夹的下面的所有东西的绝对路径
        if os.path.isfile(file_data) == True:  # os.path.isfile判断是否为文件,如果是文件,就删除.如果是文件夹.递归给del_file.
            os.remove(file_data)
        else:
            del_file(file_data)


def get_not_work(courses: list, xxt: NewXxt, console: Console, sleep_time: float = 1) -> list:
    not_work = []
    for course in courses:
        with console.status(f"[red]正在查找《{course['course_name']}》...[{course['id']}/{len(courses)}]"):
            time.sleep(sleep_time)
            try:
                works = xxt.getWorks(course["course_url"], course["course_name"])
                for work in works:
                    if work["work_status"] == "未交":
                        not_work.append({
                            "id": work["id"],
                            "work_name": work["work_name"],
                            "work_status": work["work_status"],
                            "course_name": work["course_name"]
                        })
            except Exception as e:
                console.print("[red]出现了一点小意外")
    return not_work


def show_not_work(not_work: list, console: Console) -> None:
    tb = Table("id", "作业名", "课程名称", "作业状态", border_style="blue")
    for work in not_work:
        tb.add_row(
            f"[green]{work['id']}",
            work["work_name"],
            work["course_name"],
            f"[green]{work['work_status']}",
        )
    console.rule("[blue]作业文件列表", characters="*")
    console.print(tb)
