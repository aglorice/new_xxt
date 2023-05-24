# -*- coding = utf-8 -*-
# @Time :2023/5/17 14:31
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  answer_type.py
import bs4


class AnswerType:
    @staticmethod
    def multipleChoice(item: bs4.element.Tag) -> dict:
        option = []
        option_list = item.find_all_next("li")[0:4]
        for _option in option_list:
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

    @staticmethod
    def multipleChoices(item: bs4.element.Tag) -> dict:
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

    @staticmethod
    def judgeChoice(item: bs4.element.Tag) -> dict:
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

    @staticmethod
    def comprehensive(item: bs4.element.Tag) -> dict:
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

    @staticmethod
    def shortAnswer(item: bs4.element.Tag) -> dict:
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

    @staticmethod
    def essayQuestion(item: bs4.element.Tag):
        print("论述题")

    @staticmethod
    def other(item: bs4.element.Tag):
        print("其他")

    @staticmethod
    def error():
        print("出现了错误")


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
