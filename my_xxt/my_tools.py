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


def select_works(console: Console, works: list) -> list:
    works_list = []
    if not len(works):
        return []
    while True:
        index = console.input("[yellow]请输入作业答案的id(如果是爬取多个作业，序号按照（1，2，3）英文逗号)：")
        index = index.replace(" ", "")
        index_list = index.split(",")

        for item in works:
            for choose in index_list:
                if item["work_id"] == choose:
                    works_list.append(item)
        if len(works_list):
            return works_list
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
        # 批量导出指定课程的作业
        elif index == "6":
            courses = xxt.getCourse()
            show_course(courses, console)
            course = select_course(console, courses)
            works = xxt.getWorks(course["course_url"], course["course_name"])
            show_works(works, console)

            # 爬取答案
            works = select_works(console, works)
            if works == []:
                console.print("[red]该课程下没有作业")
                continue
            i = 0
            for work in works:
                with console.status(f"[red]正在查找《{work['work_name']}》...[{i + 1}/{len(works)}]"):
                    i = i + 1
                    try:
                        if work["work_status"] == "已完成":
                            answer_list = xxt.getAnswer(work["work_url"])
                        else:
                            console.print("[red]该作业似乎没有完成")
                            continue
                        # 保存答案至answer文件
                        dateToJsonFile(answer_list, work)
                        continue
                    except Exception as e:
                        console.print("[red]出现了一点小意外", e)
            console.log("[green]爬取成功")
            continue
        # 完成指定课程的指定作业（未完成）
        elif index == "7":
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
            if work["work_status"] == "已完成" and work["isRedo"] == "no":
                console.print("[red]该作业已经完成了")
                continue
            else:
                if work["isRedo"] == "yes":
                    choose = console.input("[yellow]该作业可以重做，请确认是否要重做：（yes/no）")
                    if choose == "no":
                        continue
                    else:
                        result = xxt.redoWork(work["work_url"])
                        if result["status"] == 1:
                            console.print("[green]作业重做成功")
                        else:
                            console.print(f"[red]作业重做失败,错误原因[red]{result['msg']}[/red]")
                questions = xxt.get_question(work["work_url"])
            if not is_exist_answer_file(f"{work['id']}.json"):
                console.print("[green]没有在答案文件中匹配到对应的答案文件")
                continue
            else:
                dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                path = os.path.join(dir_path, "answers", f"{work['id']}.json")
                answer = match_answer(jsonFileToDate(path)[work["id"]], questions, xxt.randomOptions)
                show_answer(answer_list=answer, console=console)

            choose = console.input("[yellow]是否继续进行提交：（yes/no）")
            if not (choose == "yes"):
                continue
            ret = xxt.commit_work(answer, work)
            console.log(ret)
            works = xxt.getWorks(course["course_url"], course["course_name"])
            show_works(works, console)
            continue
        # 批量完成作业
        elif index == "8":
            courses = xxt.getCourse()
            show_course(courses, console)
            course = select_course(console, courses)
            works = xxt.getWorks(course["course_url"], course["course_name"])
            show_works(works, console)

            work = select_work(console, works)
            dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            path = os.path.join(dir_path, "user.json")
            users = jsonFileToDate(path)
            show_users(users, console)

            users_select = select_users(users, console)
            i = 0
            success_count = 0
            fail_count = 0
            for user in users_select:
                i = i + 1
                login_status = xxt.login(user["phone"], user["password"])
                # 判断登录成功与否
                if login_status["status"] == True:
                    courses = xxt.getCourse()
                    course = find_course(courses, work["courseId"])
                    works = xxt.getWorks(course["course_url"], course["course_name"])
                    work = find_work(works, work["work_id"])
                    # 判断是否存在作业或者课程
                    if course == {} or work == {}:
                        console.print(f"({i})  [green]{user['name']}---该用户的作业操作失败[red]该账号不存在该课程或者作业")
                        fail_count = fail_count + 1
                    else:
                        # 判断作业是什么状态
                        if work["work_status"] == "已完成":
                            console.print(f"({i})  [green]{user['name']}---该用户的作业操作失败[red]该账号已完成该作业")
                            fail_count = fail_count + 1
                            continue
                        else:
                            questions = xxt.get_question(work["work_url"])
                        # 判断是否存在答案文件
                        if not is_exist_answer_file(f"{work['id']}.json"):
                            console.print(f"({i})  [green]{user['name']}---该用户的作业操作失败[red]没有在答案文件中匹配到对应的答案文件")
                            fail_count = fail_count + 1
                            continue
                        else:
                            dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
                            path = os.path.join(dir_path, "answers", f"{work['id']}.json")
                            answer = match_answer(jsonFileToDate(path)[work["id"]], questions)
                            ret = xxt.commit_work(answer, work)
                            # 作业提交成功
                            if ret["msg"] == 'success!':
                                works = xxt.getWorks(course["course_url"], course["course_name"])
                                work = find_work(works, work["work_id"])
                                console.print(f"({i})  [green]{user['name']}---该用户的作业操作成功[blue]最终分数为{work['score']}")
                                success_count = success_count + 1
                            else:
                                console.print(f"({i})  [green]{user['name']}---该用户的作业操作失败 {ret},你可以再次尝试一次。")
                                fail_count = fail_count + 1
                                continue
                else:
                    console.print(f"({i})  [green]{user['name']}---该用户的作业操作失败[red]账号或者密码错误")
                    fail_count = fail_count + 1
            console.log(f"[yellow]一共成功{success_count},失败数为{fail_count}")
            continue
        # 退出登录
        elif index == "9":
            return
        select_error(console)


def find_course(courses: list, course_id: str) -> dict:
    for course in courses:
        # url 里面有course_id
        if course_id in course["course_url"]:
            return course
    return {}


def find_work(works: list, work_id: str) -> dict:
    for work in works:
        if work["work_id"] == work_id:
            return work
    return {}


def show_start(console: Console) -> None:
    console.rule("欢迎使用该做题脚本")
    console.print("    ███╗   ██╗███████╗██╗    ██╗        ██╗  ██╗██╗  ██╗████████╗\n \
   ████╗  ██║██╔════╝██║    ██║        ╚██╗██╔╝╚██╗██╔╝╚══██╔══╝\n \
 ██╔██╗ ██║█████╗  ██║ █╗ ██║         ╚███╔╝  ╚███╔╝    ██║\n\
  ██║╚██╗██║██╔══╝  ██║███╗██║         ██╔██╗  ██╔██╗    ██║\n\
  ██║ ╚████║███████╗╚███╔███╔╝███████╗██╔╝ ██╗██╔╝ ██╗   ██║\n\
  ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝  ", justify="center")

    console.print("[red]注意：该脚本仅供学习参考,详细信息请参考https://github.com/aglorice/new_xxt")


def show_users(users: dict, console: Console) -> None:
    tb = Table("序号", "账号", "密码", "姓名", border_style="blue")
    i = 0

    for user in users["users"]:
        tb.add_row(
            f"[green]{i + 1}",
            user["phone"],
            user["password"],
            user["name"],
        )
        i = i + 1
    console.rule("[blue]用户表", characters="*")
    console.print(tb)


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


def select_users(users: dict, console: Console) -> list:
    user_list = []
    users_id = console.input("[yellow]请选择你要完成此作业的账号 如(1,2,3) 英文逗号 全选请输入 all :")
    if users_id == "all":
        return users["users"]
    users_id = users_id.replace(" ", "")
    users_id_list = users_id.split(",")
    try:
        for user in users_id_list:
            user_list.append(users["users"][int(user) - 1])
        return user_list
    except Exception as e:
        select_error(console)


def show_menu(console: Console) -> None:
    console.rule("[green]菜单", characters="+")
    console.print("1.查看课程", highlight=True)
    console.print("2.查看当前所有答案文件", highlight=True)
    console.print("3.查询所有未完成的作业", highlight=True)
    console.print("4.清除所有答案文件", highlight=True)
    console.print("5.爬取指定作业的答案", highlight=True)
    console.print("6.批量爬取指定课程的答案", highlight=True)
    console.print("7.完成作业（请先确认是否已经爬取了你想要完成作业的答案）", highlight=True)
    console.print("8.批量完成作业完成作业（请先确认是否已经爬取了你想要完成作业的答案，请填好user.json里的账号数据）", highlight=True)
    console.print("9.退出登录", highlight=True)
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
        _path = os.path.join(path, item)
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
                console.print(f"[red]在查找课程[green]《{course['course_name']}》[/green]出现了一点小意外")
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
