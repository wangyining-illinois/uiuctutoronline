from flask import request, jsonify, render_template, flash, session, redirect, url_for, g
import uuid
from app.constants import *
from . import tutor
from app.db import POOL

@tutor.route('/tlogout')
def logout():
    session.clear()
    return redirect(url_for('tutor.tutor_login'))


@tutor.route('/tlogin', methods = ['POST', 'GET'])
def tutor_login():
    if request.method == 'POST':
        try:
            req_form = request.form
            netid = req_form.get('netid')
            error = None

            if not netid:
                error = 'netid is required'
                flash(error)
                # return jsonify(dict(error='netid is required'))

            # a basic use
            conn = POOL.connection()
            cur = conn.cursor()

            sql = "SELECT TID FROM tutors where netid = %s"
            cur.execute(sql, str(netid))
    
            if not cur.fetchone():
                error = 'netid not registered'
                flash(error)
                # return jsonify(dict(error='not registered'))
    
            password = str(req_form.get('password'))
            if not password:
                error = 'netid not registered'
                flash(error)
                # return jsonify(dict(error='password is required'))

            if error is not None:
                return render_template("tutors/login.html")

            sql = "SELECT password FROM tutors where netid = %s"
            cur.execute(sql, str(netid))
            result = cur.fetchone()[0]
            if str(result) != str(password):
                error = 'incorrect password'
                flash(error)
                return render_template("tutors/login.html")

            session.clear()
            sql = "SELECT * FROM tutors where netid = %s"
            cur.execute(sql, str(netid))

            cur.close()
            conn.close()

            tutor = cur.fetchone()
            session['username'] = tutor[2]
            session['log_type'] = 'tutor'
            session['tutor'] = tutor
            session['netid'] = netid
            g.type = 2

            return redirect(url_for("user.index"))

                # return jsonify(dict(code=CODE_PASSWORD_INVALID, msg='incorrect password'))
            # return jsonify(dict(code=CODE_SUCCESS, msg='logged in'))
        except Exception as e:
            return (str(e))

    return render_template("tutors/login.html")


@tutor.route('/tregister', methods=['POST', 'GET'])
def tutor_register():
    if request.method == 'POST':
        try:
            req_form = request.form
            netid = str(req_form.get('netid'))
            error = None
            if not netid:
                error = 'netid is required'
                flash(error)
                return 
                # return jsonify(dict(error='netid is required'))
            password = str(req_form.get('password'))
            if not password:
                error = 'password is required'
                flash(error)
                # return jsonify(dict(error='password is required'))
            tname = req_form.get('tname')
            if not tname:
                error = 'tname is required'
                flash(error)
                # return jsonify(dict(error='tutor name is required'))
            major = str(req_form.get('major'))
            if not major:
                error = 'major is required'
                flash(error)
                # return jsonify(dict(error='major is required'))
                
            if error is not None:
                return render_template("tutors/register.html")
            
            selfintro = "lazy boy, leaving nothing..." if req_form.get('selfintro') is None else req_form.get('selfintro')
            grade = "Senior" if req_form.get('grade') is None else req_form.get('grade')
            gpa = "3.8" if req_form.get('gpa') is None else req_form.get('gpa')

            m1 = 0 if req_form.get('m1') is None else 1
            m2 = 0 if req_form.get('m2') is None else 1
            m3 = 0 if req_form.get('m3') is None else 1

            t1 = 0 if req_form.get('t1') is None else 1
            t2 = 0 if req_form.get('t2') is None else 1
            t3 = 0 if req_form.get('t3') is None else 1

            w1 = 0 if req_form.get('w1') is None else 1
            w2 = 0 if req_form.get('w2') is None else 1
            w3 = 0 if req_form.get('w3') is None else 1

            th1 = 0 if req_form.get('th1') is None else 1
            th2 = 0 if req_form.get('th2') is None else 1
            th3 = 0 if req_form.get('th3') is None else 1

            f1 = 0 if req_form.get('f1') is None else 1
            f2 = 0 if req_form.get('f2') is None else 1
            f3 = 0 if req_form.get('f3') is None else 1

            s1 = 0 if req_form.get('s1') is None else 1
            s2 = 0 if req_form.get('s2') is None else 1
            s3 = 0 if req_form.get('s3') is None else 1

            su1 = 0 if req_form.get('su1') is None else 1
            su2 = 0 if req_form.get('su2') is None else 1
            su3 = 0 if req_form.get('su3') is None else 1
    
            course1 = str(req_form.get('course1'))
            course2 = str(req_form.get('course2'))
            course3 = str(req_form.get('course3'))
            course4 = ""
            course5 = ""
            # course4 = str(req_form.get('course4'))
            # course5 = str(req_form.get('course5'))

            # a basic use
            conn = POOL.connection()
            cur = conn.cursor()
    
            sql = "INSERT INTO tutors (tid, netid, tname, major, selfintro, grade, gpa, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            TID = str(uuid.uuid4())
            cur.execute(sql, (TID, netid, tname, major, selfintro, grade, gpa, password))
    
            sql = "INSERT INTO avtime (idavtime,TID,m1,m2,m3,t1,t2,t3,w1,w2,w3,th1,th2,th3,f1,f2,f3,s1,s2,s3,su1,su2,su3) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cur.execute(sql, (
            str(uuid.uuid4()), TID, m1, m2, m3, t1, t2, t3, w1, w2, w3, th1, th2, th3, f1, f2, f3, s1, s2, s3, su1, su2,
            su3))
    
            sql = "INSERT INTO tcourses (tcoursesid, course1, course2, course3, course4, course5, TID)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cur.execute(sql, (str(uuid.uuid4()), course1, course2, course3, course4, course5, TID))

            cur.close()
            conn.close()

            # return jsonify(dict(code=CODE_SUCCESS, msg='registerd'))
            flash("Register Successfully!")
            return redirect(url_for("tutor.tutor_login"))
        except Exception as e:
            return (str(e))
    
    return render_template("tutors/register.html")


@tutor.route('/tdelete', methods=['POST'])
def tutor_delete():
    try:
        req_form = request.form
        netid = req_form.get('netid')
        if not netid:
            return jsonify(dict(code=CODE_ARGS_INCOMPLETE, msg='netid is required'))

        # a basic use
        conn = POOL.connection()
        cur = conn.cursor()

        sql = "DELETE FROM tutors WHERE netid = %s"
        cur.execute(sql, str(netid))

        cur.close()
        conn.close()
        session.clear()
        g.type = None
        return redirect(url_for("tutor.tutor_login"))
    except Exception as e:
        return (str(e))


@tutor.route('/tupdate', methods=['POST', 'GET'])
def tutor_update():
    if request.method == 'POST':
        try:
            req_form = request.form
            netid = req_form.get('netid')

            conn = POOL.connection()
            cur = conn.cursor()

            sql = "SELECT TID FROM tutors where netid = %s"
            cur.execute(sql, str(netid))
            TID = (cur.fetchall())[0][0]
            password = req_form.get('password')
            if password:
                sql = "UPDATE tutors SET tname = %s WHERE password = %s"
                cur.execute(sql, (str(password), str(netid)))
            tname = req_form.get('tname')
            if tname:
                sql = "UPDATE tutors SET tname = %s WHERE netid = %s"
                cur.execute(sql, (str(tname), str(netid)))
            major = req_form.get('major')
            if major:
                sql = "UPDATE tutors SET major = %s WHERE netid = %s"
                cur.execute(sql, (str(major), str(netid)))
            selfintro = req_form.get('selfintro')
            if selfintro:
                sql = "UPDATE tutors SET selfintro = %s WHERE netid = %s"
                cur.execute(sql, (str(selfintro), str(netid)))
            grade = req_form.get('grade')
            if grade:
                sql = "UPDATE tutors SET grade = %s WHERE netid = %s"
                cur.execute(sql, (str(grade), str(netid)))
            gpa = req_form.get('gpa')
            if gpa:
                sql = "UPDATE tutors SET gpa = %s WHERE netid = %s"
                cur.execute(sql, (str(gpa), str(netid)))


            m1 = 0 if req_form.get('m1') is None else 1
            m2 = 0 if req_form.get('m2') is None else 1
            m3 = 0 if req_form.get('m3') is None else 1

            t1 = 0 if req_form.get('t1') is None else 1
            t2 = 0 if req_form.get('t2') is None else 1
            t3 = 0 if req_form.get('t3') is None else 1

            w1 = 0 if req_form.get('w1') is None else 1
            w2 = 0 if req_form.get('w2') is None else 1
            w3 = 0 if req_form.get('w3') is None else 1

            th1 = 0 if req_form.get('th1') is None else 1
            th2 = 0 if req_form.get('th2') is None else 1
            th3 = 0 if req_form.get('th3') is None else 1

            f1 = 0 if req_form.get('f1') is None else 1
            f2 = 0 if req_form.get('f2') is None else 1
            f3 = 0 if req_form.get('f3') is None else 1

            s1 = 0 if req_form.get('s1') is None else 1
            s2 = 0 if req_form.get('s2') is None else 1
            s3 = 0 if req_form.get('s3') is None else 1

            su1 = 0 if req_form.get('su1') is None else 1
            su2 = 0 if req_form.get('su2') is None else 1
            su3 = 0 if req_form.get('su3') is None else 1

            sql = "UPDATE avtime " \
                  "SET m1 = %s,m2 = %s,m3 = %s, t1 = %s,t2 = %s,t3 = %s,w1 = %s,w2 = %s,w3 = %s,th1 = %s,th2 = %s," \
                  "th3 = %s,f1 = %s,f2 = %s,f3 = %s,s1 = %s,s2 = %s,s3 = %s,su1 = %s,su2 = %s,su3 = %s WHERE TID = %s"
            cur.execute(sql, (m1, m2, m3, t1, t2, t3, w1, w2, w3, th1, th2, th3, f1, f2, f3, s1, s2, s3, su1, su2, su3, str(TID)))

            course1 = str(req_form.get('course1'))
            if course1:
                sql = "UPDATE tcourses SET course1 = %s WHERE TID = %s"
                cur.execute(sql, (str(course1), str(TID)))
            course2 = str(req_form.get('course2'))
            if course2:
                sql = "UPDATE tcourses SET course2 = %s WHERE TID = %s"
                cur.execute(sql, (str(course2), str(TID)))
            course3 = str(req_form.get('course3'))
            if course3:
                sql = "UPDATE tcourses SET course3 = %s WHERE TID = %s"
                cur.execute(sql, (str(course3), str(TID)))
            course4 = str(req_form.get('course4'))
            if course4:
                sql = "UPDATE tcourses SET course4 = %s WHERE TID = %s"
                cur.execute(sql, (str(course4), str(TID)))
            course5 = str(req_form.get('course5'))
            if course5:
                sql = "UPDATE tcourses SET course5 = %s WHERE TID = %s"
                cur.execute(sql, (str(course5), str(TID)))

            cur.close()
            conn.close()

            flash("Your Profile has updated successfully!")
            return redirect(url_for("tutor.tutor_update"))
            # return jsonify(dict(code=CODE_SUCCESS, msg='updated'))
        except Exception as e:
            return (str(e))

    conn = POOL.connection()
    cur = conn.cursor()

    netid = session.get("netid")
    if netid is None:
        flash("You need to login!")
        redirect(url_for("tutor.tutor_login"))

    sql = "SELECT * FROM tutors where netid = %s"
    cur.execute(sql, netid)
    tutorInfo = cur.fetchone()

    sql = "SELECT * FROM avtime where tid = %s"
    cur.execute(sql, tutorInfo[0])
    freetimeInfo = cur.fetchone()

    sql = "SELECT * FROM tcourses where tid = %s"
    cur.execute(sql, tutorInfo[0])
    courses = cur.fetchone()

    cur.close()
    conn.close()

    
    return render_template("tutors/self.html", tutorInfo=tutorInfo, freetimeInfo=freetimeInfo, courses=courses)
