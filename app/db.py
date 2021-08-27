import pymysql
from .config import database
from dbutils.pooled_db import PooledDB

# 5为连接池里的最少连接数，setsession=['SET AUTOCOMMIT = 1']是用来设置线程池是否打开自动更新的配置，0 为False，1 为True
POOL = PooledDB(pymysql, 5, host=database['host'], user=database['username'],
                passwd=database['password'], db=database['database'], port=database['port'], setsession=['SET AUTOCOMMIT = 1'])

# a basic use of POOL
# conn = POOL.connection()
# cur = conn.cursor()
#
# cur.close()
# conn.close()
