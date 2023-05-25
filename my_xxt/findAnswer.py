# -*- coding = utf-8 -*-
# @Time :2023/5/23 20:27
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  findAnswer.py
import difflib


def match_answer(answer_list: list, question_list: list):
    """
    更具问题寻找答案
    :param answer_list:
    :param question_list:
    :return:
    """
    answer = []
    for question in question_list:
        for item in answer_list:
            if question["id"] == item["id"]:
                if question["type"] == "单选题" or question["type"] == "多选题":
                    answer_str = find_answer(question["option"], item["option"], item["answer"])
                else:
                    answer_str = item['answer']
                answer.append({
                    "id": question["id"],
                    "title": question["title"],
                    "option": question["option"],
                    "answer": answer_str
                })
    return answer


def find_answer(question_option: list, answer_option: list, answer):
    """
    选择题匹配答案
    :param question_option:
    :param answer_option:
    :param answer:
    :return:
    """
    # 多选题
    if type(answer) == list:
        temp = []
        my_answer = ""
        for item in answer_option:
            if item.split(".")[0] in answer:
                temp.append(item)
                continue
        for item in temp:
            index = diffOption(item, question_option)
            my_answer = my_answer + question_option[index].split(".")[0]
        my_answer = "".join(sorted(my_answer))
    elif type(answer) == str:
        temp = ""
        for item in answer_option:
            if item.split(".")[0] == answer:
                temp = item
        index = diffOption(temp, question_option)
        my_answer = question_option[index][0]
    else:
        my_answer = answer
    return my_answer


def diffOption(item, options):
    """
    使用相似度来匹配对应的选项
    :param item:
    :param options:
    :return:
    """
    sample = []
    for i in options:
        temp = i.split(" ")[0]
        i = i.replace(temp, "").replace(" ", "")
        sample.append(difflib.SequenceMatcher(None, i,
                                              item.split(item[1])[1]).quick_ratio())
    return sample.index(max(sample))
