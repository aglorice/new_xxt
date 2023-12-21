# -*- coding = utf-8 -*-
# @Time :2023/5/17 14:31
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  answer_type.py
import bs4
from rich.console import Console


class AnswerType:
    @staticmethod
    def multipleChoice(item: bs4.element.Tag, console: Console) -> dict:
        try:
            option = []
            option_list = item.find_all_next("ul")[0]
            for _option in option_list:
                if _option == "\n":
                    continue
                option.append(my_replace(_option.text))
            answer = getAnswer(item)
            title = item.find_all("h3", attrs={"class": "mark_name colorDeep"})[0].text
            question_answer = {
                "id": item.attrs['data'],
                "title": title,
                "type": "单选题",
                "answer": answer,
                "option": option
            }
            return question_answer
        except Exception as e:
            console.print(f"[bold red]单选题题目解析错误[/bold red]")
            console.print(f"[bold red]错误信息:{e}[/bold red]")

    @staticmethod
    def multipleChoices(item: bs4.element.Tag, console: Console) -> dict:
        try:
            option = []
            option_list = item.find_all_next("ul")[0]
            for _option in option_list:
                if _option == "\n":
                    continue
                option.append(my_replace(_option.text))
            answer = getAnswer(item)
            title = item.find_all("h3", attrs={"class": "mark_name colorDeep"})[0].text
            question_answer = {
                "id": item.attrs['data'],
                "title": title,
                "type": "多选题",
                "answer": answer,
                "option": option
            }
            return question_answer
        except Exception as e:
            console.print(f"[bold red]多选题题目解析错误[/bold red]")
            console.print(f"[bold red]错误信息:{e}[/bold red]")

    @staticmethod
    def judgeChoice(item: bs4.element.Tag, console: Console) -> dict:
        try:
            option = []
            answer = getAnswer(item)
            title = item.find_all("h3", attrs={"class": "mark_name colorDeep"})[0].text
            question_answer = {
                "id": item.attrs['data'],
                "title": title,
                "type": "判断题",
                "answer": answer,
                "option": option
            }
            return question_answer
        except Exception as e:
            console.print(f"[bold red]判断题题目解析错误[/bold red]")
            console.print(f"[bold red]错误信息:{e}[/bold red]")

    @staticmethod
    def comprehensive(item: bs4.element.Tag, console: Console) -> dict:
        try:
            option = []
            answer = []
            answer_list = item.find_all_next("dl", attrs={"class": "mark_fill colorGreen"})[0].find_all("dd")
            for _answer in answer_list:
                answer.append(my_replace(_answer.text))
            title = item.find_all("h3", attrs={"class": "mark_name colorDeep"})[0].text
            question_answer = {
                "id": item.attrs['data'],
                "title": title,
                "type": "填空题",
                "answer": answer,
                "option": option
            }
            return question_answer
        except Exception as e:
            console.print(f"[bold red]填空题题目解析错误[/bold red]")
            console.print(f"[bold red]错误信息:{e}[/bold red]")
            console.print(f"[bold red]题目信息:{item}[/bold red]")

    @staticmethod
    def shortAnswer(item: bs4.element.Tag, console: Console) -> dict:
        try:
            option = []
            answer = item.find("dd").text
            title = item.find_all("h3", attrs={"class": "mark_name colorDeep"})[0].text
            question_answer = {
                "id": item.attrs['data'],
                "title": title,
                "type": "简答题",
                "answer": answer,
                "option": option
            }
            return question_answer
        except Exception as e:
            console.print(f"[bold red]简答题题目解析错误[/bold red]")
            console.print(f"[bold red]错误信息:{e}[/bold red]")

    @staticmethod
    def essayQuestion(item: bs4.element.Tag, console: Console):
        try:
            option = []
            answer = item.find("dd").text
            title = item.find_all("h3", attrs={"class": "mark_name colorDeep"})[0].text
            question_answer = {
                "id": item.attrs['data'],
                "title": title,
                "type": "论述题",
                "answer": answer,
                "option": option
            }
            return question_answer
        except Exception as e:
            console.print(f"[bold red]论述题题目解析错误[/bold red]")
            console.print(f"[bold red]错误信息:{e}[/bold red]")
    @staticmethod
    def programme(item: bs4.element.Tag, console: Console):
        try:
            option = []
            answer = []
            answer_list = item.find_all_next("dl", attrs={"class": "mark_fill colorGreen"})[0].find_all("dd")
            for _answer in answer_list:
                answer.append(my_replace(_answer.text))
            title = item.find_all("h3", attrs={"class": "mark_name colorDeep"})[0].text
            question_answer = {
                "id": item.attrs['data'],
                "title": title,
                "type": "编程题",
                "answer": answer,
                "option": option
            }
            return question_answer
        except Exception as e:
            console.print(f"[bold red]编程题题目解析错误[/bold red]")
            console.print(f"[bold red]错误信息:{e}[/bold red]")


    @staticmethod
    def other(item: bs4.element.Tag, console: Console):
        try:
            option = []
            answer = item.find("dd").text
            title = item.find_all("h3", attrs={"class": "mark_name colorDeep"})[0].text
            question_answer = {
                "id": item.attrs['data'],
                "title": title,
                "type": "其他",
                "answer": answer,
                "option": option
            }
            return question_answer
        except Exception as e:
            console.log(f"[bold red]其他题目解析错误[/bold red]")
            console.log(f"[bold red]错误信息:{e}[/bold red]")


    @staticmethod
    def error(item: bs4.element.Tag, console: Console):
        try:
            title_type = item.find_next("span").string.split(",")[0].replace("(", "").replace(")", "")
            console.log(f"[bold red]该题目类型[bold green]{title_type}[/bold green]还没有支持，请到本项目提交issue[/bold red]")
            return {}
        except Exception as e:
            console.log(f"[bold red]题目解析错误[/bold red]")
            console.log(f"[bold red]错误信息:{e}[/bold red]")
            return None


def my_replace(_string: str):
    if _string is None:
        return Exception
    return _string.replace("\xa0", ' ').replace("\n", "").replace(" ", "").replace("\t", "").replace(" ", "").replace(
        "\r", "")


def getAnswer(item) -> str:
    try:
        answer = item.find_all_next("span", attrs={"class": "colorGreen marginRight40 fl"})[0].text.replace(
            "正确答案: ", "")
        answer = my_replace(answer)
    except Exception as e:
        answer = item.find_all_next("span", attrs={"class": "colorDeep marginRight40 fl"})[0].text.replace("我的答案: ",
                                                                                                           "")
        answer = my_replace(answer)
    return answer
