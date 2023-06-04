# -*- coding = utf-8 -*-
# @Time :2023/5/16 17:09
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :xxt_cli
# @File :  api.py
import base64
import re
import secrets
import time
import random
from urllib import parse
from urllib.parse import urlparse

import bs4
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests as requests

from my_xxt.answer_type import AnswerType
from my_xxt.question_type import QuestionType

# 加密密钥
key = b"u2oh6Vu^HWe4_AES"

# 登录接口（post）
LOGIN_URL = "http://passport2.chaoxing.com/fanyalogin"

# 获取课程（get）
GET_COURSE_URl = "https://mooc2-ans.chaoxing.com/mooc2-ans/visit/courses/list"

# 获取课程作业（get）
GET_WORK_URL = "https://mooc1.chaoxing.com/mooc2/work/list"

# 提交作业（post）
COMMIT_WORK = "https://mooc1.chaoxing.com/work/addStudentWorkNewWeb"

# 确认提交（get）
IS_COMMIT = "https://mooc1.chaoxing.com/work/validate"

# 获取个人信息(get)
SELF_INFO = "http://passport2.chaoxing.com/mooc/accountManage"

# 获取二维码图片（get）
GET_LOGIN_QR = "https://passport2.chaoxing.com/createqr"

# 判断是否二维码登录成功(post)
IS_QR_LOGIN = "https://passport2.chaoxing.com/getauthstatus"

# 登录页面首页（get）
HOME_LOGIN = "https://passport2.chaoxing.com/login"

# 答案题目类型
answer_type = [
    {"type": "单选题", "fun": "multipleChoice", "key": "0"},
    {"type": "多选题", "fun": "multipleChoices", "key": "1"},
    {"type": "判断题", "fun": "judgeChoice", "key": "3"},
    {"type": "填空题", "fun": "comprehensive", "key": "2"},
    {"type": "简答题", "fun": "shortAnswer", "key": "4"},
    {"type": "论述题", "fun": "essayQuestion", "key": "6"},
    {"type": "其他", "fun": "other", "key": "8"},
]
# 问题题目类型
question_type = [
    {"type": "单选题", "fun": "multipleChoice"},
    {"type": "多选题", "fun": "multipleChoices"},
    {"type": "判断题", "fun": "judgeChoice"},
    {"type": "填空题", "fun": "comprehensive"},
    {"type": "简答题", "fun": "shortAnswer"},
    {"type": "论述题", "fun": "essayQuestion"},
    {"type": "其他", "fun": "other"},
]


class NewXxt:
    def __init__(self):
        # 创建一个会话实例
        self.qr_enc = None
        self.qr_uuid = None
        self.sees = requests.session()

        self.header = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                      "Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63 "

    def qr_get(self) -> None:
        """获取二维码登录key"""
        self.sees.cookies.clear()
        resp = self.sees.get(
            HOME_LOGIN, headers={"User-Agent": self.get_ua("web")}  # 这里不可以用移动端 UA 否则鉴权失败
        )
        resp.raise_for_status()
        html = BeautifulSoup(resp.text, "lxml")
        self.qr_uuid = html.find("input", id="uuid")["value"]
        self.qr_enc = html.find("input", id="enc")["value"]

        # 激活qr但忽略返回的图片bin
        resp = self.sees.get(GET_LOGIN_QR, params={"uuid": self.qr_uuid, "fid": -1})
        resp.raise_for_status()

    def qr_geturl(self) -> str:
        """合成二维码内容url"""
        return f"https://passport2.chaoxing.com/toauthlogin?uuid={self.qr_uuid}&enc={self.qr_enc}&xxtrefer=&clientid=&type=0&mobiletip="

    def login_qr(self) -> dict:
        """使用二维码登录"""
        resp = self.sees.post(IS_QR_LOGIN, data={"enc": self.qr_enc, "uuid": self.qr_uuid})
        resp.raise_for_status()
        content_json = resp.json()
        return content_json

    def login(self, phone: str, password: str) -> dict:
        """
        登录学习通
        :param phone: 手机号
        :param password: 密码
        :return: 登录结果
        """
        # 开始加密参数
        cryptor = AES.new(key, AES.MODE_CBC, key)
        phone = base64.b64encode(cryptor.encrypt(pad(phone.encode(), 16))).decode()
        cryptor = AES.new(key, AES.MODE_CBC, key)
        password = base64.b64encode(cryptor.encrypt(pad(password.encode(), 16))).decode()
        resp = self.sees.post(
            url=LOGIN_URL,
            headers={
                "Host": "passport2.chaoxing.com",
                "Origin": "http://passport2.chaoxing.com",
                "User-Agent": self.header,
            },
            data={
                'uname': phone,
                'password': password,
                't': "true",
                'validate': None,
                'doubleFactorLogin': "0",
                'independentId': "0"
            },
        )
        return resp.json()

    def getCourse(self) -> list:
        """
        获取所有的课程
        :return: 所有的课程信息
        """
        # 所有的课程信息
        course_list = []
        course = self.sees.get(
            url=GET_COURSE_URl,
            headers={
                "User-Agent": self.header,
            },
            params={
                "v": time.time(),
                "start": 0,
                "size": 500,
                "catalogId": 0,
                "superstarClass": 0,
            }
        )
        course = BeautifulSoup(course.text, "lxml")
        course_div_list = course.find_all("div", attrs={"class": "course-info"})
        i = 1
        for course_div in course_div_list:
            try:
                course_dict = {
                    "id": str(i),
                    "course_name": self.my_replace(course_div.span.string),
                    "course_url": course_div.a.attrs['href'],
                    "course_teacher": self.my_replace(
                        course_div.find_next("p", attrs={"class", "line2 color3"})["title"]),
                    "course_class": course_div.find_next("p", attrs={"class", "overHidden1"}).text
                }
            except Exception as e:
                # 先写着，万一有啥特殊情况
                course_dict = {
                    "id": str(i),
                    "course_name": self.my_replace(course_div.span.string),
                    "course_url": course_div.a.attrs['href'],
                    "course_teacher": "小明",
                    "course_class": course_div.find_next("p", attrs={"class", "overHidden1"}).text
                }
            course_list.append(course_dict)
            i = i + 1
        return course_list

    def getInfo(self) -> dict:
        info_html = self.sees.get(
            url=SELF_INFO,
            headers={
                "User-Agent": self.header,
            },
        )
        info_html_soup = BeautifulSoup(info_html.text, "lxml")
        info_html_soup = info_html_soup.find("div", attrs={"class": "infoDiv"})
        info = {
            "name": info_html_soup.find("span", attrs={"id": "messageName"})["value"],
            "student_number": info_html_soup.find("p", attrs={"class": "xuehao"}).text.replace("学号/工号:", "")
        }
        return info

    def getWorks(self, course_url: str, course_name: str) -> list:
        """
        获取一个课程的作业
        :param course_url: 课程的url
        :param course_name: 课程的名称
        :return:该课程所有的作业
        """
        works = []
        work_view = self.sees.get(
            url=course_url,
            headers={
                "User-Agent": self.header,
            },
            params={
                "v": time.time(),
                "start": 0,
                "size": 500,
                "catalogId": 0,
                "superstarClass": 0,
            }
        )
        # 解析url中的重要参数
        url_params = urlparse(work_view.url)
        work_date = parse.parse_qs(url_params.query)
        # 获取workEnc
        work_enc = BeautifulSoup(work_view.text, "lxml")
        work_enc = work_enc.find("input", id="workEnc")["value"]

        get_work_date = {
            "courseId": work_date["courseid"][0],
            "classId": work_date["clazzid"][0],
            "cpi": work_date["cpi"][0],
            "ut": "s",
            "enc": work_enc,  # workEnc
        }
        work_list = self.sees.get(
            url=GET_WORK_URL,
            params=get_work_date,
            headers={
                "Host": "mooc1.chaoxing.com",
                "Referer": "https://mooc2-ans.chaoxing.com/",
                "User-Agent": self.header,
            },
            allow_redirects=True
        )
        work_li_list_soup = BeautifulSoup(work_list.text, "lxml")
        work_li_list = work_li_list_soup.find_all("li")

        i = 1
        for work in work_li_list:
            url_params = urlparse(work.attrs['data'])
            work_date = parse.parse_qs(url_params.query)
            _work = {
                "work_id": str(i),
                "id": work_date["workId"][0],
                "work_name": work.find_next('p').string,
                "work_status": work.find_next("p").find_next("p").string,
                "work_url": work.attrs['data'],
                "course_name": course_name,
                "isRedo": self.getIsRedo(work.attrs['data']),
                "score": self.getWorkScore(work.attrs['data'])
            }
            i = i + 1
            works.append(_work)
        return works

    def getWorkScore(self, work_url: str) -> str:
        """
        获取一个作业的分数
        :param work_url: 作业的url
        :return:
        """
        result = self.sees.get(
            url=work_url,
            headers={
                "User-Agent": self.header,
            },
        )
        result_view = BeautifulSoup(result.text, "lxml")
        try:
            result_view_soup = result_view.find("span", attrs={"class": "resultNum"})
            return result_view_soup.text
        except Exception as e:
            try:
                result_view_soup = result_view.find("p", attrs={"class": "Finalresult"})
                result_view_soup = result_view_soup.find("span")
                return result_view_soup.text
            except Exception as e:
                return "无"

    def getIsRedo(self, work_url: str) -> str:
        """
        获取作业重做状态
        :param work_url:
        :return:
        """
        result = self.sees.get(
            url=work_url,
            headers={
                "User-Agent": self.header,
            },
        )
        try:
            result_view = BeautifulSoup(result.text, "lxml")
            result_view_soup = result_view.find("a", attrs={"class": "redo"})
            if "重做" in result_view_soup:
                return "yes"
        except Exception as e:
            return "no"

    def getAnswer(self, work_url: str) -> list:
        """
        爬取已完成作业的答案
        :param work_url:
        :return:
        """
        work_answer = []
        work_answer_view = self.sees.get(
            url=work_url,
            headers={
                "User-Agent": self.header,
            },
        )
        work_view_soup = BeautifulSoup(work_answer_view.text, "lxml")
        work_view = work_view_soup.find_all("div", attrs={"class": "marBom60 questionLi"})
        _answer_type = AnswerType()
        for item in work_view:
            title_type = item.find_next("span").string.split(",")[0].replace("(", "").replace(")", "")
            # 根据选项去自动调用对应的方法来解析数据
            func_name = self.selectFunc(title_type, answer_type)
            func = getattr(_answer_type, func_name)
            work_answer.append(func(item))
        return work_answer

    def create_from(self, work_url: str) -> dict:
        """
        构造提交作业所需要的数据
        :param work_url:
        :return:
        """
        work_view_html = self.sees.get(
            url=work_url,
            headers={
                "User-Agent": self.header,
            },
        )
        work_view_html_soup = BeautifulSoup(work_view_html.text, "lxml")
        commit_date = work_view_html_soup.find("form")["action"]
        # 解析form表单的url中的重要参数
        url_params = urlparse(commit_date)
        work_date = parse.parse_qs(url_params.query)
        # 查找构造表单所需的数据
        input_date = work_view_html_soup.find_all("input")
        commit_date_form = {}
        # 解析做作业的页面的url
        do_work_url_params = urlparse(work_view_html.url)
        do_work_params = parse.parse_qs(do_work_url_params.query)
        try:
            for _input in input_date:
                _key = re.findall(r'id="(.*?)"', str(_input))
                _value = str(_input.attrs['value'])
                commit_date_form[_key[0]] = _value
                commit_date_form = commit_date_form
        except Exception as e:
            commit_date_form = commit_date_form
        commit_date = {
            "_classId": work_date["_classId"][0],
            "courseid": work_date["courseid"][0],
            "token": work_date["token"][0],
            "totalQuestionNum": work_date["totalQuestionNum"][0],
            "ua": "pc",
            "formType": "post",
            "saveStatus": "1",
            "version": "1",
            "workRelationId": do_work_params["workId"][0],
            "workAnswerId": do_work_params["answerId"][0],
            "standardEnc": do_work_params["standardEnc"][0]
        }
        commit_date = dict(commit_date_form, **commit_date)
        return commit_date

    def commit_before(self, commit_date: dict) -> str:
        """
        在作业提交提交之前需要发送一个请求
        :param commit_date:
        :return:
        """
        ret = self.sees.get(
            url=IS_COMMIT,
            params={
                "courseId": commit_date['courseId'],
                "classId": commit_date["classId"],
                "cpi": commit_date["cpi"]
            },
            headers={
                "User-Agent": self.header,
            },
        )
        return ret.text

    def commit_work(self, answer: list, work: dict) -> dict:
        """
        提交作业
        :param answer:
        :param work:
        :return:
        """
        commit_from = self.create_from(work_url=work["work_url"])
        params = self.create_params(commit_from)
        data = self.create_from_data(commit_from, answer)
        self.commit_before(commit_from)
        ret = self.sees.post(
            url=COMMIT_WORK,
            params=params,
            data=data,
            headers={
                "User-Agent": self.header,
            },
        )
        return ret.json()

    def get_question(self, work_url: str, params=None) -> list:
        """
        获取未完成作业的题目
        :param params:
        :param work_url:
        :return:
        """
        work_question = []
        work_question_view = self.sees.get(
            url=work_url,
            headers={
                "User-Agent": self.header,
            },
            params=params,
        )
        work_view_soup = BeautifulSoup(work_question_view.text, "lxml")
        work_view = work_view_soup.find_all("div", attrs={"class": "padBom50 questionLi"})
        _question_type = QuestionType()
        for item in work_view:
            title_type = item.find_next("span").string.split(",")[0].replace("(", "").replace(")", "")
            func_name = self.selectFunc(title_type, question_type)
            func = getattr(_question_type, func_name)
            work_question.append(func(item))
        return work_question

    @staticmethod
    def my_replace(_string: str):
        if _string is None:
            return Exception
        return _string.replace("\xa0", ' ').replace("\n", "").replace(" ", "").replace("\t", "").replace(" ", "")

    @staticmethod
    def selectFunc(type_question: str, _type: list) -> str:
        for item in _type:
            if item["type"] == type_question:
                return item["fun"]
        return "error"

    @staticmethod
    def allQuestionId(answer: list) -> str:
        """
        将代做的题目id连接在一起
        :return: 连接好的id
        """
        answer_id_all = ""
        for item in answer:
            answer_id_all = answer_id_all + item['id'] + ','
        return answer_id_all

    @staticmethod
    def create_params(commit_from: dict) -> dict:
        params = {
            "_classId": commit_from["_classId"],
            "courseid": commit_from["courseid"],
            "token": commit_from["token"],
            "totalQuestionNum": commit_from["totalQuestionNum"],
            "ua": commit_from["ua"],
            "formType": commit_from["formType"],
            "saveStatus": commit_from["saveStatus"],
            "version": commit_from["version"],
        }
        return params

    @staticmethod
    def get_ua(ua_type: str) -> str:
        """获取UA"""
        match ua_type:
            case "mobile":
                return f"Dalvik/2.1.0 (Linux; U; Android {random.randint(9, 12)}; MI{random.randint(10, 12)} Build/SKQ1.210216.001) (device:MI{random.randint(10, 12)}) Language/zh_CN com.chaoxing.mobile/ChaoXingStudy_3_5.1.4_android_phone_614_74 (@Kalimdor)_{secrets.token_hex(16)}"
            case "web":
                return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35"
            case _:
                raise NotImplementedError

    def create_from_data(self, commit_from: dict, answer: list) -> dict:
        """
        将答案构造成提交所需要的格式
        :param commit_from:
        :param answer:
        :return:
        """
        commit_from_1 = {
            "courseId": commit_from["courseId"],
            "classId": commit_from["classId"],
            "knowledgeId": commit_from["knowledgeId"],
            "cpi": commit_from["cpi"],
            "workRelationId": commit_from["workRelationId"],
            "workAnswerId": commit_from["workAnswerId"],
            "jobid": commit_from["jobid"],
            "standardEnc": commit_from["standardEnc"],
            "enc_work": commit_from["token"],
            "totalQuestionNum": commit_from["totalQuestionNum"],
            "pyFlag": commit_from["pyFlag"],
            "answerwqbid": self.allQuestionId(answer),
            "mooc2": commit_from["mooc2"],
            "randomOptions": commit_from["randomOptions"],
        }
        from_date_2 = {}
        for item in answer:
            if "单选题" in item["title"]:
                key1 = "answertype" + item["id"]
                from_date_2[key1] = 0
                key2 = "answer" + item["id"]
                from_date_2[key2] = item["answer"]
            elif "填空题" in item["title"]:
                key3 = "answertype" + item["id"]
                from_date_2[key3] = 2
                key4 = "tiankongsize" + item["id"]
                from_date_2[key4] = len(item["answer"])
                for answer_item in range(1, len(item["answer"]) + 1):
                    _key = "answerEditor" + item["id"] + str(answer_item)
                    from_date_2[_key] = "<p>" + item["answer"][answer_item - 1].split(")")[1] + "<br/></p>"
            elif "判断题" in item["title"]:
                key5 = "answertype" + item["id"]
                from_date_2[key5] = 3
                key6 = "answer" + item["id"]
                if item["answer"] == "错":
                    _answer = "false"
                else:
                    _answer = "true"
                from_date_2[key6] = _answer
            elif "简答题" in item["title"]:
                key6 = "answertype" + item["id"]
                from_date_2[key6] = 4
                key7 = "answer" + item["id"]
                from_date_2[key7] = item["answer"]
            elif "论述题" in item["title"]:
                key8 = "answertype" + item["id"]
                from_date_2[key8] = 6
                key9 = "answer" + item["id"]
                from_date_2[key9] = item["answer"]
            elif "多选题" in item["title"]:
                key9 = "answertype" + item["id"]
                from_date_2[key9] = 1
                key10 = "answer" + item["id"]
                from_date_2[key10] = item["answer"]
            elif "其他" in item['title']:
                key11 = "answertype" + item["id"]
                from_date_2[key11] = 8
                key12 = "answer" + item["id"]
                from_date_2[key12] = item["answer"]

        commit_from_1 = dict(from_date_2, **commit_from_1)
        return commit_from_1
