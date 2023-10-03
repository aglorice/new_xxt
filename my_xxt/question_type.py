# -*- coding = utf-8 -*-
# @Time :2023/5/23 20:34
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  question_type.py
import bs4


class QuestionType:
    @staticmethod
    def multipleChoice(item: bs4.element.Tag) -> dict:
        option = []
        title = item.find("h3", attrs={"class": "mark_name colorDeep fontLabel"}).text
        option_list = item.find_all("div", attrs={"class": "clearfix answerBg"})
        for _option in option_list:
            _option = _option["aria-label"]
            option.append(_option.replace("选择", ""))
        question = {
            "id": item.attrs['data'],
            "title": my_replace(title),
            "type": "单选题",
            "option": option,
            "answer": None
        }
        return question

    @staticmethod
    def multipleChoices(item: bs4.element.Tag) -> dict:
        option = []
        title = item.find("h3", attrs={"class": "mark_name colorDeep fontLabel"}).text
        option_list = item.find_all("div", attrs={"class": "clearfix answerBg"})
        for _option in option_list:
            _option = _option["aria-label"]
            option.append(_option.replace("选择", ""))
        question = {
            "id": item.attrs['data'],
            "title": my_replace(title),
            "type": "多选题",
            "option": option,
            "answer": None
        }
        return question

    @staticmethod
    def judgeChoice(item: bs4.element.Tag) -> dict:
        title = item.find("h3", attrs={"class": "mark_name colorDeep fontLabel"}).text
        question_answer = {
            "id": item.attrs['data'],
            "title": my_replace(title),
            "type": "判断题",
            "answer": None,
            "option": None
        }
        return question_answer

    @staticmethod
    def comprehensive(item: bs4.element.Tag) -> dict:
        title = item.find("h3", attrs={"class": "mark_name colorDeep fontLabel"}).text
        question_answer = {
            "id": item.attrs['data'],
            "title": my_replace(title),
            "type": "填空题",
            "answer": None,
            "option": None
        }
        return question_answer

    @staticmethod
    def shortAnswer(item: bs4.element.Tag) -> dict:
        title = item.find("h3", attrs={"class": "mark_name colorDeep fontLabel"}).text
        question_answer = {
            "id": item.attrs['data'],
            "title": my_replace(title),
            "type": "简答题",
            "answer": None,
            "option": None
        }
        return question_answer

    @staticmethod
    def essayQuestion(item: bs4.element.Tag):
        title = item.find("h3", attrs={"class": "mark_name colorDeep fontLabel"}).text
        question_answer = {
            "id": item.attrs['data'],
            "title": my_replace(title),
            "type": "论述题",
            "answer": None,
            "option": None
        }
        return question_answer

    @staticmethod
    def programme(item: bs4.element.Tag):
        title = item.find("h3", attrs={"class": "mark_name colorDeep fontLabel"}).text
        question_answer = {
            "id": item.attrs['data'],
            "title": my_replace(title),
            "type": "编程题",
            "answer": None,
            "option": None
        }
        return question_answer

    @staticmethod
    def other(item: bs4.element.Tag):
        title = item.find("h3", attrs={"class": "mark_name colorDeep fontLabel"}).text
        question_answer = {
            "id": item.attrs['data'],
            "title": my_replace(title),
            "type": "其他",
            "answer": None,
            "option": None
        }
        return question_answer

    @staticmethod
    def error(item: bs4.element.Tag):
        print("该题型暂不支持")


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
