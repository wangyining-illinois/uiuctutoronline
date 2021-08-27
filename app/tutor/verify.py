# coding=utf-8
# author: Zerun Zhao, Shuoyang Fan
import pymongo
import pymysql.cursors
import re
from app.db import POOL

def my_split(s):
    temp = re.compile("([a-zA-Z]+)([0-9]+)")
    res = temp.match(s).groups()
    return res

def calculate_grade(collection,term, instructor,subject,num,standing,rating,culmulative_gpa,course_grade):
    start = calculate_grade_flag(collection,term, instructor,subject,num)
    if (start == False):
        return 0
    elif course_grade=='A+':
        return 100
    else:
        cursordis = collection.aggregate([{"$match":{"YearTerm": term, "Subject": subject, 'Number': num, 'Primary Instructor': instructor}},
        {"$group": { "_id": "","count_A+": { "$sum": {"$toInt" :'$A+'}},"count_A": { "$sum": {"$toInt" :'$A'}}, "count_A-": { "$sum": {"$toInt" :'$A-'}},
        "count_B+": { "$sum": {"$toInt" :'$B+'}}, "count_B": { "$sum": {"$toInt" :'$B'}},"count_B-": { "$sum": {"$toInt" :'$B-'}},
                "count_C+": { "$sum": {"$toInt" :'$C+'}},"count_C": { "$sum": {"$toInt" :'$C'}}, "count_C-": { "$sum": {"$toInt" :'$C-'}},
                     "count_D+": { "$sum": {"$toInt" :'$D+'}},"count_D": { "$sum": {"$toInt" :'$D'}}, "count_D-": { "$sum": {"$toInt" :'$D-'}},
                "count_F": { "$sum": {"$toInt" :'$F'}}, "count_W": { "$sum": {"$toInt" :'$W'}}}}])

        ## dict
        x_list =  list(cursordis)[0]
        x_list["_id"] = 0
        x_list_sum = sum(x_list.values())

        final_list = x_list
        final_list["total"]= x_list_sum
        for i in final_list:
            final_list[i] = final_list[i]/final_list["total"]

        list_cm = []
        sum_1 = 0
        for j in final_list:
            sum_1 =sum_1+ final_list[j]
            list_cm.append(sum_1)

        list_cm[len(list_cm)-1]=1

        check_score_dict = {'A+': 0, 'A': 1, 'A-': 2, 'B+': 3, 'B': 4, 'B-': 5,'C+': 6, 'C': 7, 'C-': 8,'D+': 9, 'D': 10, 'D-': 11,'F':12,'W': 13}

        score = (((1 -(list_cm[check_score_dict[course_grade]]))+(1 -(list_cm[1+check_score_dict[course_grade]])))/2)*50

        score += (culmulative_gpa/4)*20
        check_standing_dict = {"Freshman": 0, "Sophomore": 1, "Junior": 2, "Senior": 3}
        standing_dist = abs(check_standing_dict[standing])
        score += (standing_dist) * 5
        score += (1-standing_dist/3)*15
        score += rating *3
        return score


def calculate_grade_flag(collection,term, instructor,subject,num):
    cursordis = collection.aggregate([{"$match":{"YearTerm": term, "Subject": subject, 'Number': num, 'Primary Instructor': instructor}},
    {"$group": { "_id": "","count_A+": { "$sum": {"$toInt" :'$A+'}},"count_A": { "$sum": {"$toInt" :'$A'}}, "count_A-": { "$sum": {"$toInt" :'$A-'}},
    "count_B+": { "$sum": {"$toInt" :'$B+'}}, "count_B": { "$sum": {"$toInt" :'$B'}},"count_B-": { "$sum": {"$toInt" :'$B-'}},
             "count_C+": { "$sum": {"$toInt" :'$C+'}},"count_C": { "$sum": {"$toInt" :'$C'}}, "count_C-": { "$sum": {"$toInt" :'$C-'}},
             "count_F": { "$sum": {"$toInt" :'$F'}}, "count_W": { "$sum": {"$toInt" :'$W'}}}}])


    check_list_length =  len(list(cursordis))
    if (check_list_length == 0):
        return False
    else:
        return True

def calculate_grade_boolean(grade):
    if grade >= 70:
        return True
    else:
        return False

def check_instructor(term,instructor,course_grade,coursename,netid):
    connection = pymongo.MongoClient("localhost", 27017)
    database = connection.gpa
    collection = database.uiucgpa
    connection = POOL.connection()
    cur = connection.cursor()

    subject,num=my_split(coursename)
    num=int(num)

    sql = "SELECT grade FROM tutors where netid = %s"
    cur.execute(sql, str(netid))
    standing = cur.fetchall()
    if len(standing) == 0:
        standing = 'Junior'
    else:
        standing = standing[0][0]

    sql = "SELECT rating FROM tutors natural join comments where netid = %s"
    cur.execute(sql, str(netid))
    rating=cur.fetchall()
    if len(rating) == 0:
        rating = 3
    else:
        rating= rating[0][0]
    rating=int(rating)

    sql = "SELECT gpa FROM tutors where netid = %s"
    cur.execute(sql, str(netid))
    gpa = cur.fetchall()
    if len(gpa) == 0:
        gpa = 3.7
    else:
        gpa = gpa[0][0]
    gpa=int(gpa)

    return calculate_grade_boolean(calculate_grade(collection,term,instructor,subject,num,standing,rating,gpa,course_grade))

if __name__ == '__main__':
    """
    #check_instructtor function为接口， term, instructor, course_grade, coursename, netid从外部传入, 输入的coursename格式为CS411，字母全大写，中间无空格
    #1.	老师的名字（对应 csv 的 primary instructor）
    2.	课程名称 （ex：“CS241”）
    3.	上课学期 （ 对应 csv 的 YearTerm）
    ## 最好可以做一个下拉菜单提供选项 ex “2020-sp， 2018-fa“
    4.	 上课得分 （对应csv 的“A+”，“A”等）
    ## 最好可以做一个下拉菜单提供选项 ex “A， A-“
    """
    ## 测试样例
    term = "2020-sp"
    instructor = "Kang, Yoonjung"
    course_grade = 'A-'
    netid = "yiningw6"
    coursename = "AAS100"

    print("result is:",check_instructor(term,instructor,course_grade,coursename,netid))
