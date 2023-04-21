# -*- coding = utf-8 -*-
# @Time :2023/3/12 18:38
# @Author :小岳
# @Email  :401208941@qq.com
# @PROJECT_NAME :new_xxt
# @File :  new_xxt.py
import difflib
import json
import os
import pickle
import re
import time
from urllib import parse
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import lxml

import requests as requests

from deciphering import encrypto

LOGIN_URL = "http://passport2.chaoxing.com/fanyalogin"
MOOC_URL = "http://i.mooc.chaoxing.com"


class XcxyXxt:
    def __init__(self, phone, password, fid, refer):
        # 加密手机号和密码
        crypto_data = self.decrypto(phone, password)
        # 加密后的结果
        self.phone = crypto_data['phone']
        self.password = crypto_data['pwd']

        self.header = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                      "Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.63 "

        # url参数
        self.fid = fid  # 学校的唯一id
        self.refer = refer  # 学校的学习通网站的url

        self.menus_list = ""
        self.courses = ""
        self.work_list = ""
        self.question_list = ""
        self.commit_date = ""
        self.commit_date_form = ""

        self.sees = requests.session()

    def decrypto(self, phone, password):
        return encrypto(phone, password)

    def Login(self,batch = False):
        # 进入到自己学院的学习通
        self.sees.post(
            url=LOGIN_URL,
            headers={
                "Host": "passport2.chaoxing.com",
                "Origin": "http://passport2.chaoxing.com",
                "User-Agent": self.header,
            },
            data={
                'fid': self.fid,
                'uname': self.phone,
                'password': self.password,
                'refer': self.refer,
                't': "true",
                'validate': None,
                'doubleFactorLogin': "0",
                'independentId': "0"
            },
        )

        # 进入到慕课的学习空间
        print("[info]---获取菜单信息中...")
        view = self.sees.get(
            url=MOOC_URL,
            headers={
                "User-Agent": self.header,
            },
            params={
                "t": time.time()
            }

        )
        soup = BeautifulSoup(view.text, "lxml")
        if "用户登录" in str(soup):
            print("[info]---登录失败，请检查账号或者密码是否正确")
            if not batch:
                exit(0)
            else:
                return 0

        # 获取菜单
        self.menus_list = self.getMenus(soup)

    def saveCookie(self):
        with open('../../Desktop/NewXxt/cookie.txt', 'wb') as f:
            pickle.dump(self.sees.cookies, f)

    def getCookie(self):
        with open('../../Desktop/NewXxt/cookie.txt', 'rb') as f:
            self.sees.cookies.update(pickle.load(f))

    def getMenus(self, soup):
        """
        获取菜单列表信息
        :param soup: BeautifulSoup解析的结果
        :return menus_list: 菜单列表
        """
        menus_list = []
        menus_a = soup.find_all('li')
        print("[info]---成功获取菜单信息")
        print("====================菜单=====================")
        for menu_a in menus_a:
            try:
                menu = {
                    'name': menu_a.em.string.replace('\r', "").replace('\n', "").replace('\t', ""),
                    'url': re.findall(r',(\'.*\')', menu_a.a.attrs['href'])[0].replace("'", "")
                }
            except Exception as e:
                menu = {
                    'name': menu_a.em.string.replace('\r', "").replace('\n', "").replace('\t', ""),
                    'url': menu_a.a.attrs['href']
                }
            menus_list.append(menu)

            print(f"[option]---{menu['name']}")
        print("=======================================")

        return menus_list

    def dateToJsonCatalog(self, answer_id: str, _dict: dict):

        try:
            to_dict = {
                answer_id: _dict
            }
        except Exception as e:
            to_dict = {
                answer_id: "55555555"
            }
            print(f"[error]---保存信息时发生了错误{e}")
        # json.dumps 序列化时对中文默认使用的ascii编码.想输出真正的中文需要指定ensure_ascii=False
        json_data = json.dumps(to_dict, ensure_ascii=False)
        folder = 'answers'

        file = os.getcwd().replace("xcxy_xxt.py", "") + "\\" + folder + "\\" + f"{answer_id}.json"
        if not os.path.exists(folder):
            os.makedirs(folder)
        with open(file, 'w', encoding="utf-8") as f_:
            f_.write(json_data)

    def dateToJsonFile(self, path: str, _dict: dict):
        """
        将答案写入文件保存为json格式
        :param path: 文件的路径
        :param _dict: 代写入的字典
        :return:
        """
        to_dict = {
            path: _dict
        }
        # json.dumps 序列化时对中文默认使用的ascii编码.想输出真正的中文需要指定ensure_ascii=False
        json_data = json.dumps(to_dict, ensure_ascii=False)
        with open(path, 'w', encoding="utf-8") as f_:
            f_.write(json_data)

    def jsonFileToDate(self, file):
        with open(file, 'r', encoding="utf-8") as f_:
            json_data = json.loads(f_.read())
        return json_data

    def baseListGetUrl(self, menu_key):
        """
        根据功能寻找url
        :param menu_key:
        :return: url
        """
        for menu in self.menus_list:
            if menu["name"] == menu_key:
                return menu["url"]

    def baseCourseGetUrl(self, course_key: str):
        """
        根据课程名称匹配url
        :param course_key: 课程名称
        :return:
        """
        for course in self.courses:
            if course["course_name"] == course_key:
                return course["course_url"]
        print(f"[info]---没有发现该{course_key},请检查是否加入了该课程")

    def baseWorkGetUrl(self, work_name: str):
        """
        根据作业匹配url
        :param work_name: 作业的名称
        :return:
        """
        for work in self.work_list:
            if work["work_name"] == work_name:
                return work["work_url"]
        print(f"[info]---没有发现该{work_name},请检查是否存在该作业")

    def baseNotDoneWorkGetAnswer(self, work_list):
        for item, value in work_list.items():
            if len(value) != 0:
                for _item in value:
                    # 解析url中的重要参数
                    print("====================批量提取答案======================")
                    url_params = urlparse(_item["work_url"])
                    work_date = parse.parse_qs(url_params.query)
                    answer_id = work_date["workId"][0]
                    self.getCourseWork(item)
                    work_answer = self.getWorkAnswer(_item['work_name'], status=True)
                    if work_answer is None:
                        print(f"[error]---获取{item}课程的{_item['work_name']}时失败")
                        print("==========================================")
                        continue
                    self.dateToJsonCatalog(answer_id, work_answer)
                    print("==========================================")

    def getCourseDate(self):
        """
        获取所有的课程信息
        :return:
        """
        courses = []
        get_course_url_cookies = str(self.baseListGetUrl("课程"))
        get_course_url = "http://mooc1-1.chaoxing.com/visit/courselistdata"
        print("[info]---获取课程信息中...")
        self.sees.get(
            url=get_course_url_cookies,
            headers={
                "User-Agent": self.header,
            },

        )
        course = self.sees.post(
            url=get_course_url,
            headers={
                "User-Agent": self.header,
            },
            data={
                "courseType": 1,
                "courseFolderId": 0,
                "baseEducation": 0,
                "superstarClass": None,
                "courseFolderSize": 0
            }
        )

        course = BeautifulSoup(course.text, "lxml")
        course_div_list = course.find_all("div", attrs={"class": "course-info"})
        print("[info]---成功获取课程信息")
        print("====================课程======================")
        for course_div in course_div_list:
            try:
                course_dict = {
                    "course_name": course_div.span.string,
                    "course_url": course_div.a.attrs['href'],
                    "course_teacher": course_div.find_next("p").find_next("p").string.replace("\xa0", ' '),
                    "course_class": course_div.find_next("p").find_next("p").find_next("p").string.replace("班级：", '')
                }
            except Exception as e:
                print(f"[info]---课程教师信息可能缺失{e}")
                course_dict = {
                    "course_name": course_div.span.string,
                    "course_url": course_div.a.attrs['href'],
                    "course_teacher": course_div.find_next("p").find_next("p").string,
                    "course_class": course_div.find_next("p").find_next("p").find_next("p").string.replace("班级：", '')
                }
            courses.append(course_dict)
            print(f"[option]---{course_dict['course_name']}")
        print("=======================================")
        self.courses = courses

    def getCourseWork(self, course_name: str, sleep_time=0,batch = False):
        """
        获取该课程下的所有作业
        :param sleep_time:
        :param course_name:课程名称
        :return None:
        """
        work_list = []
        GET_WORK_URL = "https://mooc1.chaoxing.com/mooc2/work/list"
        print(f"[info]---获取{course_name}的作业中...")
        course_url = self.baseCourseGetUrl(course_name)
        if course_url is None:
            return None
        time.sleep(sleep_time)
        work_view = self.sees.get(
            url=course_url,
            headers={
                "User-Agent": self.header,
            },
            allow_redirects=True
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
        work_html = self.sees.get(
            url=GET_WORK_URL,
            params=get_work_date,
            headers={
                "Host": "mooc1.chaoxing.com",
                "Referer": "https://mooc2-ans.chaoxing.com/",
                "User-Agent": self.header,
            },
            allow_redirects=True
        )
        if "无权限的操作" in work_html.text:
            print("[error]---爬取课程作业的时候没有权限")
            if not batch:
                exit(0)
            else:
                return 0
        elif "无效的用户" in work_html.text:
            print("[error]---无效的用户！")
            if not batch:
                exit(0)
            else:
                return 0
        else:
            print(f"[info]---获取{course_name}的作业成功")
        work_li_list_soup = BeautifulSoup(work_html.text, "lxml")
        work_li_list = work_li_list_soup.find_all("li")
        for work in work_li_list:
            _work = {
                "work_name": work.find_next('p').string,
                "work_status": work.find_next("p").find_next("p").string,
                "work_url": work.attrs['data']
            }
            work_list.append(_work)
        self.work_list = work_list
        return work_list

    def getAllNotDoneWork(self):
        work_list_dict = {}
        print("====================查询未完成的作业======================")
        for courses in self.courses:
            _work_list = []
            work_list = self.getCourseWork(courses["course_name"], sleep_time=2)
            # 提取未批阅的作业
            for item in work_list:
                if item["work_status"] == "未交":
                    print(f"[info]---成功发现《{courses['course_name']}》的--{item['work_name']}--未交")
                    _work_list.append(item)

            work_list_dict[courses["course_name"]] = _work_list
            print("=======================================")
        print("=======================================")
        return work_list_dict

    def getWorkAnswer(self, work_name: str, status=False):
        """
        根据作业名字将答案爬取下来
        :param status: 判断是否为批量提取答案还是单个
        :param work_name:作业名称
        :return work_answer: 作业的答案
        """

        work_answer = []
        # 判断作业是否已经完成
        if not self.is_completed(work_name):
            print("[error]---作业的提供者并未完成作业")
            if status:
                return None
            else:
                exit(0)
        work_url = self.baseWorkGetUrl(work_name)
        work_answer_view = self.sees.get(
            url=work_url,
            headers={
                "User-Agent": self.header,
            },
        )
        work_view_soup = BeautifulSoup(work_answer_view.text, "lxml")
        work_view = work_view_soup.find_all("div", attrs={"class": "marBom60 questionLi"})

        for _work_answer in work_view:
            _title = ""
            option = []
            answer = []
            title_type = _work_answer.find_next("span").string.split(",")[0].replace("(", "").replace(")", "")
            # 判断题目是否存在于p标签

            title = _work_answer.find_all("h3", attrs={"class": "mark_name colorDeep"}) + _work_answer.find_all("p")
            _title = self.connectTitle(title, title_type)
            if title_type == "单选题":
                option_list = _work_answer.find_all_next("li")[0:4]
                for _option in option_list:
                    option.append(_option.text.replace(" ", ""))
            elif title_type == "多选题":
                option_list = _work_answer.find_all_next("ul")[0]
                for _option in option_list:
                    if _option == "\n":
                        continue
                    option.append(_option.text.replace(" ", ""))
            else:
                option = None
            if title_type == "简答题":
                answer = _work_answer.find_next("dd").string
            if title_type == "单选题" or title_type == "判断题":
                try:
                    answer = _work_answer.find_all_next("span", attrs={"class": "colorGreen marginRight40 fl"})[
                        0].text.replace("正确答案: ", "").replace("\n", "").replace("\r", "").replace("\t", "").replace(" ",
                                                                                                                    "")
                except Exception as e:
                    print(f"[error]---发生了错误{e},这道题还没有公布正确答案,正在获取已完成作业的者的答案")
                    answer = _work_answer.find_all_next("span", attrs={"class": "colorDeep marginRight40 fl"})[
                        0].text.replace("我的答案: ", "").replace("\n", "").replace("\r", "").replace("\t", "").replace(" ",
                                                                                                                    "")
                    if answer is None:
                        print(f"[error]---无法找到正确答案！！")
                        exit(0)
            if title_type == "多选题":
                try:
                    d_answer = _work_answer.find_next("span").find_next("span").contents[1]
                except Exception as e:
                    d_answer = _work_answer.find_next("span", attrs={"class": "colorDeep marginRight40 fl"}).contents[1]
                answer.append(d_answer)
            if title_type == "填空题":
                answer_list = _work_answer.find_all_next("dl", attrs={"class": "mark_fill colorGreen"})[0].find_all(
                    "dd")
                for _answer in answer_list:
                    answer.append(_answer.text.replace(" ", ""))

            work_answer.append({
                "id": _work_answer.attrs['data'],
                "title": _title,
                "type": title_type,
                "answer": answer,
                "option": option
            })
        print(f"[info]---成功获取了{work_name}的答案")
        return work_answer

    def is_completed(self, work_name: str):
        """
        判断使用者的需要完成的作业的完成状态
        :param work_name:作业名称
        :return: 是否完成该作业
        """
        for work in self.work_list:
            if work["work_name"] == work_name and work["work_status"] == "已完成":
                return True
        return False

    def getWorkView(self, work_name, file, batch=False):
        DO_WORK_URL = "https://mooc1.chaoxing.com/mooc2/work/dowork"
        # 判断需要完成作业的状态
        question_list = []
        _question_list = []
        if self.is_completed(work_name=work_name):
            print(f"[info]---你的作业<<{work_name}>>已经完成了,已经不需要完成了✌️✌️✌️")
            if batch == False:
                exit(0)
            else:
                return

        work_view_html = self.sees.get(
            url=self.baseWorkGetUrl(work_name),
            headers={
                "User-Agent": self.header,
            },
            allow_redirects=True
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
                self.commit_date_form = commit_date_form
        except Exception as e:
            self.commit_date_form = commit_date_form

        self.commit_date = {
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
        work_view = work_view_html_soup.find_all("div", attrs={"class": "padBom50 questionLi"})
        print(f"[info]---成功获取了<<{work_name}>>的题目")
        for item in work_view:
            _title = ""
            option = []
            _id = item.attrs['data']
            title_type = item.find_next("span").string.split(",")[0].replace("(", "").replace(")", "")
            title = item.find_all("h3", attrs={"class": "mark_name colorDeep fontLabel"}) + item.find_all("p")
            _title = self.connectTitle(title, title_type)

            if title_type == "多选题" or title_type == "单选题":
                option_list = item.find("div", attrs={"class": "stem_answer"})
                option_list = option_list.find_all("div", attrs={"class": "clearfix answerBg"})
                for _option in option_list:
                    temp = _option.text.split("\n")
                    option.append(temp[1] + "." + temp[2])
            else:
                option = None

            answer = self.findAnswer(file, item.attrs['data'], option, title_type)
            question_list.append({
                "id": _id,
                "title": _title,
                "option": option,
                "answer": answer
            })
        self.question_list = question_list
        print(f"[info]---成功获取到了该作业的答案")

    def connectTitle(self, title, title_type):
        _title = ""
        for item in title:
            _title = _title + str(item.text).replace("\n", "").replace("\r", "").replace("\t", "").replace(" ",
                                                                                                           "").replace(
                " ", "")
        _title = _title.split("。")[0]
        if title_type == "判断题":
            _title = _title + "。()"
        else:
            _title = _title + "。"
        return _title

    def diffOption(self, item, options):
        sample = []
        for i in options:
            sample.append(difflib.SequenceMatcher(None, i, item).quick_ratio())
        return sample.index(max(sample))

    def findAnswer(self, file, title_id, option, title_type):
        answer = ""
        temp = ""
        _question_dict = self.jsonFileToDate(file)[file]
        for _question in _question_dict:
            if _question['id'] == title_id:
                if title_type == "选择题" or title_type == "单选题":
                    for item in _question["option"]:
                        if _question["answer"] in item:
                            temp = item
                    index = self.diffOption(temp, _question["option"])
                    answer = option[index].split(".")[0]
                elif title_type == "多选题":
                    temp = []
                    answer = ""
                    for item in _question["option"]:
                        if item.split(".")[0] in _question["answer"][0]:
                            temp.append(item)
                            continue
                    for item in temp:
                        index = self.diffOption(item, option)
                        answer = answer + option[index].split(".")[0]
                else:
                    answer = _question["answer"]
        if answer is None:
            print(f"[error]---请检查答案提供者的答案是否合理")
            exit(0)
        return answer

    def allQuestionId(self):
        """
        将代做的题目id连接在一起
        :return: 连接好的id
        """
        answer_id_all = ""
        for item in self.question_list:
            answer_id_all = answer_id_all + item['id'] + ','
        return answer_id_all

    def answerToformDate(self):
        from_date_2 = {}
        for item in self.question_list:
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
                    from_date_2[_key] = "<p>" + item["answer"][answer_item - 1].split(" ")[1] + "<br/></p>"
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

        return from_date_2

    def findResultNum(self, work_name):
        result = self.sees.get(
            url=self.baseWorkGetUrl(work_name),
            headers={
                "User-Agent": self.header,
            },
        )
        result_view = BeautifulSoup(result.text, "lxml")
        try:
            result_view_soup = result_view.find("span", attrs={"class": "resultNum"})
            return result_view_soup.text
        except Exception as e:
            return "待批阅"

    def completedWork(self, work_name, batch=False):
        if batch:
            return
        # https://mooc1.chaoxing.com/work/validate?courseId=204924252&classId=73792554&cpi=269513930
        is_commit = "https://mooc1.chaoxing.com/work/validate"
        commit_answer = "https://mooc1.chaoxing.com/work/addStudentWorkNewWeb"
        # 1.确认提交
        is_commit_result = self.sees.get(
            url=is_commit,
            params={
                "courseId": self.commit_date_form['courseId'],
                "classId": self.commit_date_form["classId"],
                "cpi": self.commit_date_form["cpi"]
            },
            headers={
                "User-Agent": self.header,
            },
        )
        if "3" in is_commit_result.text:
            print("[info]---答案提交已经就绪")

        from_date_1 = {
            "courseId": self.commit_date_form["courseId"],
            "classId": self.commit_date_form["classId"],
            "knowledgeId": self.commit_date_form["knowledgeId"],
            "cpi": self.commit_date_form["cpi"],
            "workRelationId": self.commit_date["workRelationId"],
            "workAnswerId": self.commit_date["workAnswerId"],
            "jobid": self.commit_date_form["jobid"],
            "standardEnc": self.commit_date_form["standardEnc"],
            "enc_work": self.commit_date["token"],
            "totalQuestionNum": self.commit_date["totalQuestionNum"],
            "pyFlag": self.commit_date_form["pyFlag"],
            "answerwqbid": self.allQuestionId(),
            "mooc2": self.commit_date_form["mooc2"],
            "randomOptions": self.commit_date_form["randomOptions"],
        }
        from_date_2 = self.answerToformDate()
        from_date = dict(from_date_1, **from_date_2)
        params = {
            "_classId": self.commit_date["_classId"],
            "courseid": self.commit_date["courseid"],
            "token": self.commit_date["token"],
            "totalQuestionNum": self.commit_date["totalQuestionNum"],
            "ua": self.commit_date["ua"],
            "formType": self.commit_date["formType"],
            "saveStatus": self.commit_date["saveStatus"],
            "version": self.commit_date["version"],
        }

        commit_answer = self.sees.post(
            url=commit_answer,
            params=params,
            data=from_date,
            headers={
                "User-Agent": self.header,
            },
        )

        if "success" in commit_answer.text:
            print(f"[info]---作业已完成，最终的分数为{self.findResultNum(work_name)}")
        else:
            print("[error]---请重新运行一次！！！")


def batchWork(file, course_name, work_name, fid, refer):
    with open(file, 'r', encoding="utf-8") as f_:
        json_data = json.loads(f_.read())['user']
    for item in json_data:
        user = XcxyXxt(phone=item["phone"], password=item["password"], fid=fid, refer=refer)
        if user.Login(batch=True) == 0:
            continue
        user.getCourseDate()
        if user.getCourseWork(course_name, batch=True) == 0:
            continue
        user.getWorkView(work_name, "answer.json", batch=True)
        user.completedWork(work_name=work_name, batch=True)
        print(f"《《《《《《成功完成了{item['phone']}的作业》》》》》》")
