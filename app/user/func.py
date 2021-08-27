# -*- coding: utf-8 -*-
from flask import request, render_template, flash, session, g, redirect, url_for
import uuid
import datetime
import functools

from app.db import POOL
from . import user


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(*args, **kw):
        if g.user is None:
            return redirect(url_for('user.user_login'))
        return view(*args, **kw)

    return wrapped_view


# user 查看 tutor 详细页面
@user.route('/u_check_totor/<netid>', methods=['GET', 'POST'])
@login_required
def user_check_tutor(netid=None):
    UID = session.get('user')[0]
    sql = "SELECT netid, tname, major, grade, gpa, state FROM user_tutor NATURAL JOIN tutors WHERE UID = %s"

    conn = POOL.connection()
    cur = conn.cursor()

    cur.execute(sql, UID)
    tutors = cur.fetchall()

    is_his_tutor = 0
    for tutor in tutors:
        if tutor[0] == netid and tutor[5] == 0:
            is_his_tutor = 3
            break
        elif tutor[0] == netid and tutor[5] == 1:
            is_his_tutor = 1
            break
        elif tutor[0] == netid and tutor[5] == 2:
            is_his_tutor = 2
            break

    # tutor_info = {}
    sql = "SELECT TID, netid, tname, major, selfIntro, grade, gpa FROM tutors WHERE netid = %s"
    cur.execute(sql, str(netid))
    info = cur.fetchone()

    if info is None:
        flash("Tutor id not exists.")
        return redirect(url_for("user.index"))

    sql = "SELECT uname, text, rating FROM users NATURAL JOIN contract NATURAL JOIN comments WHERE TID = %s"
    cur.execute(sql, info[0])

    cur.close()
    conn.close()

    comments = list(cur.fetchall())
    # for comment in comments:
    #     comment = list(comment)
    #     comment[2] = int(comment[2])

    return render_template("user/check_tutor.html", netid=netid, is_his_tutor=is_his_tutor, tutor_info=info,
                           comments=comments)


# user申请tutor
@user.route('/uapply', methods=['POST'])
@login_required
def user_apply():
    try:
        req_form = request.form
        user = session.get('user')
        UID = user[0]
        TID = req_form.get('netid')

        sql = "INSERT INTO user_tutor VALUES (%s, %s, %s, 0)"

        conn = POOL.connection()
        cur = conn.cursor()

        cur.execute(sql, (str(uuid.uuid4()), str(UID), str(TID)))

        cur.close()
        conn.close()

        flash("Apply Successfully!")
        return redirect(url_for("user.user_show_states"))
    except Exception as e:
        return (str(e))


# user显示所有申请的信息以及 user_tutor 之间的状态
@user.route('/ushowstates', methods=['POST', 'GET'])
@login_required
def user_show_states():
    user = session.get('user')
    if user is None:
        flash("You need to login to finish this operation")
        session.clear()
        g.type = None
        g.user = None
        g.tutor = None
        return redirect(url_for('user.user_login'))
    UID = user[0]

    try:
        # req_form = request.form
        # UID = req_form.get('uid')
        sql = "SELECT netid, tname, major, grade, gpa, state FROM user_tutor NATURAL JOIN tutors WHERE UID = %s"

        conn = POOL.connection()
        cur = conn.cursor()

        cur.execute(sql, UID)
        tutors = cur.fetchall()

        cur.close()
        conn.close()
    except Exception as e:
        return (str(e))

    return render_template("user/my_tutors.html", tutors=tutors)


# user评论tutor
@user.route('/ucomment', methods=['POST'])
@login_required
def user_comment():
    try:
        UID = session.get('user')[0]
        req_form = request.form
        text = req_form.get('text')
        rating = req_form.get('rating')
        TID = req_form.get('tid')
        sql = "INSERT INTO comments VALUES (%s, %s, %s, %s)"
        CID = str(uuid.uuid4())

        conn = POOL.connection()
        cur = conn.cursor()

        cur.execute(sql, (CID, str(text), str(rating), datetime.datetime.now()))
        sql = "INSERT INTO contract VALUES (%s, %s, %s, %s)"
        cur.execute(sql, (str(uuid.uuid4()), str(UID), CID, str(TID)))
        sql = "SELECT netid FROM tutors where TID = %s"
        cur.execute(sql, TID)
        T_netid = str(cur.fetchone()[0])

        cur.close()
        conn.close()

        return redirect(url_for("user.user_check_tutor", netid=T_netid))
    except Exception as e:
        return (str(e))


# user搜索tutor
@user.route('/usearch', methods=['POST'])
@login_required
def user_search(course, user_avls):
    try:
        # req_form = request.form
        # netid = req_form.get('netid')

        # get user's courses and avtimes
        # course = req_form.get('course')
        times = ['m1', 'm2', 'm3', 't1', 't2', 't3', 'w1', 'w2', 'w3', 'th1', 'th2', 'th3', 'f1', 'f2', 'f3', 's1',
                 's2', 's3',
                 'su1', 'su2', 'su3']

        # user_avls = []
        # for i in range(21):
        #     user_avls.append(0) if req_form.get(times[i]) is None else user_avls.append(1)
        # sql get all tutors with the same course as the user
        sql = "SELECT TID from tcourses WHERE course1 = %s OR course2 = %s OR course3 = %s OR course4 = %s OR course5 = %s"

        conn = POOL.connection()
        cur = conn.cursor()

        cur.execute(sql, (course, course, course, course, course))
        TIDs = cur.fetchall()

        # for loop get tutors with the same avtime
        suitable_TID = []
        for tid in TIDs:
            TID = tid[0]
            for i in range(len(times)):
                sql = "SELECT " + times[i] + " FROM avtime WHERE TID = %s"
                cur.execute(sql, TID)
                avl = int(cur.fetchall()[0][0])
                if (avl == 1 and user_avls[i] == 1):
                    suitable_TID.append(TID)
                    break

        if len(suitable_TID) == 0:
            return None
            # return jsonify(dict(code=CODE_NO_RESULT))

        # order by rating
        sql = "SELECT DISTINCT TID FROM tutors NATURAL JOIN contract NATURAL JOIN comments GROUP BY TID ORDER BY avg(rating) DESC"
        cur.execute(sql)
        TIDs = cur.fetchall()
        re_TID = []
        for tid in TIDs:
            TID = tid[0]
            if TID in suitable_TID:
                re_TID.append(TID)
        sql = "SELECT DISTINCT TID FROM tutors"
        cur.execute(sql)
        TIDs = cur.fetchall()
        for tid in TIDs:
            TID = tid[0]
            if TID in suitable_TID and TID not in re_TID:
                re_TID.append(TID)

        tutor_info = []
        for TID in re_TID:
            sql = "SELECT TID, netid, tname, major, selfIntro, grade, gpa FROM tutors WHERE TID = %s"
            cur.execute(sql, TID)
            a = cur.fetchall()[0]
            sql = "SELECT text, rating FROM contract NATURAL JOIN comments WHERE TID = %s"
            cur.execute(sql, TID)
            b = cur.fetchall()
            if not b:
                b = ''
            tutor_info.append((a, b))

        cur.close()
        conn.close()

        return tutor_info
        # return jsonify(dict(code=CODE_SUCCESS))
    except Exception as e:
        return (str(e))
