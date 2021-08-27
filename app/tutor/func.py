# -*- coding: utf-8 -*-

from flask import request, jsonify, render_template, flash, session, redirect, url_for, g
from . import tutor

from app.db import POOL
from app.tutor.verify import check_instructor
from app.tutor.verify import my_split
import pymongo


# tutor显示所有申请的 user 信息以及 user_tutor 之间的状态
@tutor.route('/tshowstates', methods=['GET'])
def tutor_show_states():
    TID = session.get('tutor')[0]

    try:
        # req_form = request.form
        # TID = req_form.get('tid')

        # a basic use
        conn = POOL.connection()
        cur = conn.cursor()

        sql = "SELECT netid FROM tutors  WHERE TID = %s"
        cur.execute(sql, TID)
        netid = cur.fetchone()[0]

        sql = "SELECT id, UID, uname, major, grade, state FROM user_tutor NATURAL JOIN users WHERE TID = %s"
        cur.execute(sql, TID)
        stus = cur.fetchall()

        cur.close()
        conn.close()
        # return jsonify(dict(code=CODE_SUCCESS, msg='success'))
    except Exception as e:
        return (str(e))
    return render_template("tutors/my_students.html", stus=stus, netid=netid)

# tutor处理请求
@tutor.route('/thandleuser', methods=['POST'])
def tutor_handle_user():
    try:
        req_form = request.form
        id = req_form.get('id')
        op = req_form.get('op')

        conn = POOL.connection()
        cur = conn.cursor()

        sql = "UPDATE user_tutor SET state = %s WHERE id = %s;"
        cur.execute(sql, (str(op), str(id)))

        cur.close()
        conn.close()

        return redirect(url_for("tutor.tutor_show_states"))
    except Exception as e:
        return (str(e))

@tutor.route('/mycomments', methods=['GET'])
def tutor_show_comments():
    TID = session.get('tutor')[0]

    # a basic use
    conn = POOL.connection()
    cur = conn.cursor()



    sql = "SELECT uname, text, rating FROM users NATURAL JOIN contract NATURAL JOIN comments WHERE TID = %s"
    cur.execute(sql, TID)
    comments = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("tutors/my_comments.html", comments=comments)


@tutor.route('/verify', methods=['POST'])
def verify():
    req_form = request.form

    netid = request.form['netid']
    term = request.form['term']
    instructor = request.form['instructor']
    course_grade = request.form['course_grade']
    course_name = request.form['course_name']

    result = check_instructor(term, instructor, course_grade, course_name, netid)

    return jsonify(success=result)

@tutor.route('/findInspector', methods=['GET'])
def search_instructor():
    term = request.args.get("term")
    coursename = request.args.get("coursename")

    connection = pymongo.MongoClient("localhost", 27017)
    database = connection.gpa
    collection = database.uiucgpa
    subject, num = my_split(coursename)
    num=int(num) #这步有可能需要删除，看database
    x = collection.find({"YearTerm": term, "Subject": subject, 'Number': num})
    y = []
    for i in x:
        if i['Primary Instructor'] in y:
            continue
        y.append(i['Primary Instructor'])

    connection.close()
    return jsonify(y)


if __name__ == '__main__':
    '''
    search_instructor 为接口
    输入是 term 和 coursename （verify的 输入） 
    返回一个满足条件的所有instructors 的 list
    我们希望用这个函数来实现当tutor register时能下拉菜单选择instructor的功能。如果返回为空，则提示 Invalid Input
    '''
    term = "2020-sp"
    coursename = "AAS100"
    print(search_instructor(term,coursename))

