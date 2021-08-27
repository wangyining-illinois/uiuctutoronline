# coding=utf-8
# author:Haoyu Wang, Yining Wang
import uuid
from flask import flash, render_template, g, session, redirect, url_for, request
from app.user.func import user_search
from app.user.recommend import recommend
from . import user
from app.db import POOL


@user.route('/verify', methods=['POST'])
def verify():
    req_form = request.form
    courseName = req_form['course']
    return courseName


@user.route('/', methods=['GET', 'POST'])
def index():
    recommend_tutor = []
    if g.type == 1 and request.form.get('course') is None:
        # default recommend tutor
        UID = session.get('user')[0]
        recommend_tutor = recommend(UID)

    if request.method == 'POST':
        req_form = request.form

        course = req_form.get('course')
        if course is None:
            flash("please input the course name")
            render_template('user/index.html')

        # get user's courses and avtimes
        course = req_form.get('course')
        times = ['m1', 'm2', 'm3', 't1', 't2', 't3', 'w1', 'w2', 'w3', 'th1', 'th2', 'th3', 'f1', 'f2', 'f3', 's1',
                 's2', 's3',
                 'su1', 'su2', 'su3']

        user_avls = []
        for i in range(21):
            user_avls.append(0) if req_form.get(times[i]) is None else user_avls.append(1)

        tutor_info = user_search(course, user_avls)

        return render_template("user/index.html", tutor_info=tutor_info, recommend_tutor=recommend_tutor)

    return render_template('user/index.html', recommend_tutor=recommend_tutor)


@user.route('/ulogout')
def logout():
    session.clear()
    g.type = None
    g.user = None
    return redirect(url_for('user.user_login'))


@user.before_app_request
def load_logged_in_user():
    netid = session.get('netid')

    if netid is None:
        g.user = None
        g.type = None
    else:
        if session['log_type'] == 'user':
            g.type = 1  # 1: stu
            g.user = session.get('user')
        elif session['log_type'] == 'tutor':
            g.type = 2  # 2: tutor
            g.tutor = session.get('tutor')


@user.route('/ulogin', methods=['POST', 'GET'])
def user_login():
    if request.method == 'POST':
        try:
            req_form = request.form
            netid = req_form.get('netid')
            error = None
            if not netid:
                error = 'netid is required'
                flash(error)
                # return jsonify(dict(code=CODE_ARGS_INCOMPLETE, msg='netid is required'))
            password = req_form.get('password')
            if not password:
                error = 'password is required'
                flash(error)
                # return jsonify(dict(code=CODE_ARGS_INCOMPLETE, msg='password is required'))
            sql = "SELECT password FROM Users where netid = %s"

            # a basic use
            conn = POOL.connection()
            cur = conn.cursor()

            cur.execute(sql, str(netid))

            result = cur.fetchall()
            corr_password = result[0][0]
            if corr_password == password:
                session.clear()
                sql = "SELECT * FROM Users where netid = %s"
                cur.execute(sql, str(netid))

                user = cur.fetchone()
                session['username'] = user[2]
                session['log_type'] = 'user'
                session['user'] = user
                session['netid'] = netid
                g.type = 1
                # flash("Login successful!")
                return redirect(url_for("user.index"))

            cur.close()
            conn.close()

        except Exception as e:
            return (str(e))

    return render_template("user/login.html")


@user.route('/uregister', methods=['POST', 'GET'])
def user_register():
    if request.method == 'POST':
        try:
            req_form = request.form
            netid = req_form.get('netid')
            error = None

            if not netid:
                error = 'netid is required'
                flash(error)
                # return jsonify(dict(code=CODE_ARGS_INCOMPLETE, msg='netid is required'))

            uname = req_form.get('uname')
            if not uname:
                error = 'user name is required'
                flash(error)
                # return jsonify(dict(code=CODE_ARGS_INCOMPLETE, msg='user name is required'))

            major = req_form.get('major')
            if not major:
                error = 'major is required'
                flash(error)
                # return jsonify(dict(code=CODE_ARGS_INCOMPLETE, msg='major is required'))

            password = req_form.get('password')
            if not password:
                error = 'password is required'
                flash(error)
                # return jsonify(dict(code=CODE_ARGS_INCOMPLETE, msg='password is required'))

            if error is None:
                selfintro = req_form.get('selfintro')
                grade = req_form.get('grade')
                sql = "INSERT INTO Users (uid, netid, uname, major, selfintro, grade, password) VALUES (%s, %s, %s, %s, %s, %s, %s)"

                conn = POOL.connection()
                cur = conn.cursor()

                cur.execute(sql, (
                    str(uuid.uuid4()), str(netid), str(uname), str(major), str(selfintro), str(grade), str(password)))

                cur.close()
                conn.close()

                # return jsonify(dict(code=CODE_SUCCESS, msg='registerd'))

                flash("Register Successfully!")
                return redirect(url_for("user.user_login"))
        except Exception as e:
            return (str(e))

    return render_template('user/register.html')


@user.route('/udelete', methods=['POST'])
def user_delete():
    try:
        req_form = request.form
        netid = req_form.get('netid')
        sql = "DELETE FROM Users WHERE netid = %s"

        conn = POOL.connection()
        cur = conn.cursor()

        cur.execute(sql, str(netid))

        cur.close()
        conn.close()

        # return jsonify(dict(code=CODE_SUCCESS, msg='deleted'))
    except Exception as e:
        return (str(e))


@user.route('/uupdate', methods=['POST', 'GET'])
def user_update():
    if request.method == 'POST':
        try:
            req_form = request.form
            netid = req_form.get('netid')
            sql = "SELECT password FROM Users where netid = %s"

            conn = POOL.connection()
            cur = conn.cursor()

            cur.execute(sql, str(netid))

            # corr_password = (cur.fetchall())[0][0]
            uname = req_form.get('uname')
            if uname:
                sql = "UPDATE Users SET uname = %s WHERE netid = %s"
                cur.execute(sql, (str(uname), str(netid)))

            major = req_form.get('major')
            if major:
                sql = "UPDATE Users SET major = %s WHERE netid = %s"
                cur.execute(sql, (str(major), str(netid)))

            selfintro = req_form.get('selfintro')
            if selfintro:
                sql = "UPDATE Users SET selfintro = %s WHERE netid = %s"
                cur.execute(sql, (str(selfintro), str(netid)))

            grade = req_form.get('grade')
            if grade:
                sql = "UPDATE Users SET grade = %s WHERE netid = %s"
                cur.execute(sql, (str(grade), str(netid)))

            cur.close()
            conn.close()

            flash("Modify Successfully!")
            redirect(url_for("user.index"))
            # return jsonify(dict(code=CODE_SUCCESS, msg='updated'))
        except Exception as e:
            return (str(e))

    conn = POOL.connection()
    cur = conn.cursor()

    netid = session.get("netid")
    if netid is None:
        flash("You need to login!")
        redirect(url_for("user.user_login"))

    sql = "SELECT * FROM Users where netid = %s"
    cur.execute(sql, netid)
    userInfo = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("user/self.html", user=userInfo)

# @user.route('/usearchb', methods=['POST'])
# def search_best():
#     try:
#         req_form = request.form
#         courses = req_form.get('courses')
#         if not courses:
#             return jsonify(dict(code=CODE_ARGS_INCOMPLETE, msg='courses is required'))
#         sql = "SELECT t.tname, t.selfintro, t.gpa, c.text, t.availtime FROM Tutors t join Comments c on t.tid = c.tid " \
#               "where t.tid in (select c.tid from Comments c group by c.tid " \
#               "having avg(c.rating) >= all (select avg(c.rating) from Comments c group by c.tid)) and t.courses = %s"
#
#         cur.execute(sql, str(courses))
#
#         results = cur.fetchall()
#         l = []
#         for i in results:
#             dict = {}
#             dict['name'] = i[0]
#             dict['selfintro'] = i[1]
#             dict['gpa'] = i[2]
#             dict['text'] = i[3]
#             dict['availtime'] = i[4]
#             l.append(dict)
#         return jsonify(l)
#     except Exception as e:
#         return (str(e))
