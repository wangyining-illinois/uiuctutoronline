# coding=utf-8
# author:Haoyu Wang, Yining Wang
from flask import jsonify
from app.constants import *
import math
import operator
from app.db import POOL


def recommend(UID=None):
    if UID is None:
        return None
    try:
        conn = POOL.connection()
        cur = conn.cursor()

        sql_all_users = "SELECT DISTINCT UID FROM contract WHERE UID <> %s"
        cur.execute(sql_all_users, UID)
        all_uids = cur.fetchall()

        # avg(r_a)
        sql_avrating = "SELECT AVG(rating) FROM comments NATURAL JOIN contract group by UID having UID = %s"
        cur.execute(sql_avrating, UID)
        r_a = cur.fetchall()

        # user一节课都没上过的情况 返回rating最高的3个tutor
        if not r_a:
            sql_top = "SELECT TID FROM contract NATURAL JOIN comments GROUP BY TID ORDER BY avg(rating) DESC LIMIT 3"
            cur.execute(sql_top)
            recommendations = cur.fetchall()

            recommend_tutor = []
            sql = "SELECT netid, tname, major, grade, gpa, selfIntro FROM tutors WHERE TID = %s"
            for t in recommendations:
                t = t[0]
                cur.execute(sql, str(t))
                result = cur.fetchall()[0]
                recommend_tutor.append(result)
            cur.close()
            conn.close()
            return recommend_tutor
        r_a = r_a[0][0]

        sim = {}
        r_b = {}
        # calculate sim
        for uid in all_uids:
            UID1 = uid[0]
            sql_findtid = "SELECT TID FROM contract WHERE TID IN (SELECT TID FROM contract WHERE UID = %s) AND UID = %s"
            cur.execute(sql_findtid, (UID, UID1))
            tids = cur.fetchall()
            # r_b
            cur.execute(sql_avrating, UID1)
            r_b[UID1] = cur.fetchall()[0][0]
            sum0 = 0
            sum1 = 0
            sum2 = 0
            for tid in tids:
                TID = tid[0]
                # r_ap
                sql_r_ap = "SELECT rating FROM comments NATURAL JOIN contract WHERE UID = %s AND TID = %s"
                cur.execute(sql_r_ap, (UID, TID))
                r_ap = float(cur.fetchall()[0][0])
                # r_ap: float, r_a: Demical 类型不兼容
                # sum1 += (r_ap -  r_a)**2
                sum1 += (r_ap - float(r_a)) ** 2
                # r_bp
                cur.execute(sql_r_ap, (UID1, TID))
                r_bp = float(cur.fetchall()[0][0])
                # sum2 += (r_bp -  r_b[UID1])**2
                sum2 += (r_bp - float(r_b[UID1])) ** 2
                # r_ap, r_bp
                # sum0 += (r_ap - r_a) * (r_bp - r_b[UID1])
                sum0 += (r_ap - float(r_a)) * (r_bp - float(r_b[UID1]))
            sum0 = math.exp(sum0)
            sum1 = math.exp(math.sqrt(sum1))
            sum2 = math.exp(math.sqrt(sum2))
            sim[UID1] = sum0 / (sum1 * sum2)
        # calculate pred
        pred = {}
        sql_find_tutors_not_used_a = "SELECT DISTINCT TID FROM contract WHERE TID NOT IN (SELECT TID FROM contract WHERE UID = %s)"
        # sql_find_tutors_not_used_a = "SELECT DISTINCT TID FROM user_tutor WHERE TID NOT IN (SELECT TID FROM user_tutor WHERE UID = %s)"
        cur.execute(sql_find_tutors_not_used_a, UID)
        tids_not_a = cur.fetchall()

        for tid in tids_not_a:
            TID = tid[0]
            sql_findb = "SELECT UID FROM contract WHERE TID = %s"
            cur.execute(sql_findb, TID)
            b = cur.fetchall()
            sum0 = 0
            sum1 = 0
            for uid in b:
                UID1 = uid[0]
                sql_find_r_bp = "SELECT rating FROM comments NATURAL JOIN contract WHERE UID = %s AND TID = %s"
                cur.execute(sql_find_r_bp, (UID1, TID))
                r_bp = float(cur.fetchall()[0][0])
                sum0 += sim[UID1] * (r_bp - float(r_b[UID1]))
                sum1 += sim[UID1]
            pred[TID] = float(r_a) + sum0 / sum1


        len_pred = len(pred)
        if len_pred >= 3:
            recommendations = dict(sorted(pred.items(), key=operator.itemgetter(1), reverse=True)[:3])
        else:
            recommendations = dict(sorted(pred.items(), key=operator.itemgetter(1), reverse=True)[:len_pred])

            if len_pred == 1:
                sql_top = "SELECT TID FROM contract NATURAL JOIN comments WHERE TID <> %s GROUP BY TID ORDER BY avg(rating) DESC LIMIT 2"
                a = list(recommendations.keys())
                cur.execute(sql_top, str(a[0]))
                result = cur.fetchall()
                for tid_in_result in result:
                    tid_in_result = tid_in_result[0]
                    recommendations[tid_in_result] = 0
            elif len_pred == 2:
                sql_top = "SELECT TID FROM contract NATURAL JOIN comments WHERE TID <> %s and TID <> %s GROUP BY TID ORDER BY avg(rating) DESC LIMIT 1"
                a = list(recommendations.keys())
                cur.execute(sql_top, (str(a[0]), str(a[1])))
                result = cur.fetchall()
                for tid_in_result in result:
                    tid_in_result = tid_in_result[0]
                    recommendations[tid_in_result] = 0
            elif len_pred == 0:
                sql_top = "SELECT TID FROM contract NATURAL JOIN comments GROUP BY TID ORDER BY avg(rating) DESC LIMIT 3"
                cur.execute(sql_top)
                result = cur.fetchall()
                for tid_in_result in result:
                    tid_in_result = tid_in_result[0]
                    recommendations[tid_in_result] = 0
        t_id = list(recommendations.keys())
        recommend_tutor = []
        sql = "SELECT netid, tname, major, grade, gpa, selfIntro FROM tutors WHERE TID = %s"
        for t in t_id:
            cur.execute(sql, str(t))
            result = cur.fetchall()[0]
            recommend_tutor.append(result)
        cur.close()
        conn.close()
        return recommend_tutor
    except Exception as e:
        return (str(e))
