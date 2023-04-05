from xcxy_xxt import XcxyXxt

# 已完成该作业的账号
phone = ""
password = ""

# 未完成作业的账号和密码
_phone = ""
_password = ""

# 学校的学习通id
fid = 2397  # 选填
refer = "http://scxcc.fanya.chaoxing.com/login/auth"  # 选填

work_name = "单元一、二、三课后作业.xls"
course_name = "建筑工程质量验收与资料"

if __name__ == '__main__':
    # """查询所有未作的作业，并在已完成的答案中提取正确答案并保存在answer文件中"""
    # user_1 = XcxyXxt(phone=phone, password=password, fid=fid, refer=refer)
    # user_2 = XcxyXxt(phone=_phone, password=_password, fid=fid, refer=refer)
    # user_1.Login()
    # user_1.getCourseDate()
    # user_2.Login()
    # user_2.getCourseDate()
    # work_list = user_2.getAllNotDoneWork()  # 获取所有课程未作的作业
    # user_1.baseNotDoneWorkGetAnswer(work_list)  # 根据未做的作业来寻找正确的答案

    """查询指定的作业并完成它"""
    print("<<<<======================================================>>>>")
    user_1 = XcxyXxt(phone=phone, password=password, fid=fid, refer=refer)
    user_1.Login()
    user_1.getCourseDate()
    user_1.getCourseWork(course_name)
    answer = user_1.getWorkAnswer(work_name)
    user_1.dateToJsonFile("1.json", answer)
    print("<<<<======================================================>>>>\n\n\n")
    print("<<<<======================================================>>>>")
    user_2 = XcxyXxt(phone=_phone, password=_password, fid=fid, refer=refer)
    user_2.Login()
    user_2.getCourseDate()
    user_2.getCourseWork(course_name)
    user_2.getWorkView(work_name, "1.json")
    user_2.completedWork(work_name=work_name)
    print("<<<<======================================================>>>>")
