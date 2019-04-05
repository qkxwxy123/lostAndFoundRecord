from flask import Flask,request
import json
import time,datetime
import pymysql
import logging
import logging.config


app = Flask(__name__)
db = pymysql.connect('localhost' , 'root' , 'qkx123' , 'swu_Assistant' , charset = "utf8")

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("lostAndFoundRecord")

def db_exec(sql):
    cursor = db.cursor()
    try:
        db.ping(reconnect=True)
        cursor.execute(sql)
        db.commit()
        return cursor
    except:
        db.rollback()
    finally:
        db.close()

def query_function(sql , pageSize , pageNo):
    cursor = db.cursor()
    try:
        db.ping(reconnect=True)
        cursor.execute(sql)

        if cursor:

            res_debug = '尝试查询记录'
            logger.info(res_debug)

            results = cursor.fetchall()
            result = {}
            count = 1

            for row in results:
                d_result = {}
                d_result['id'] = row[0]                                      #本地row[0]:id   row[1]:created_time  row[2] :phoneNumber
                d_result['text'] = row[3]                                    #row[3]:  text
                s_time = row[1].strftime("%Y-%m-%d %H:%M:%S")
                d_result['pubTime'] = s_time
                result[count] = d_result
                count += 1

            result['curPageSize'] = pageSize
            result['curPageNo'] = pageNo
            response = {}
            response['status'] = 200
            response['message'] = 'Success'
            response['data'] = result

            res_debug2 = '查询成功'
            logger.info(res_debug2)

            return response
        else:
            res_debug2 = '查询失败'
            logger.info(res_debug2)

            response = {}
            response['status'] = 500
            response['message'] = 'Error'
            response['data'] = None
            return response
    except:
        db.rollback()
    finally:
        db.close()

@app.route('/addLostFoundRecord' , methods = ["POST"])
def addLostFoundRecord():
    phoneNumber = request.args.get('phoneNumber')
    text = request.args.get('text')
    sql = "insert into swuassistant (phoneNumber , text) values ('%s' , '%s')" % (phoneNumber , text)

    phoneNumber_debug = '传入参数phoneNumber :' + phoneNumber
    text_debug = '传入参数text :' + text
    sql_debug = '传入sql :' + sql

    logger.info(phoneNumber_debug)
    logger.info(text_debug)
    logger.info(sql)

    pro_debug = '尝试执行addLostFoundRecord'
    logger.info(pro_debug)

    ret = db_exec(sql)

    if ret:
        res_debug = '执行成功'
        logger.info(res_debug)

        sql_2 = "select max(id) from swuassistant"

        sql2_debug = '传入返回插入记录的sql_id : ' + sql_2
        logger.info(sql2_debug)

        cursor = db.cursor()
        try:
            db.ping(reconnect=True)
            cursor.execute(sql_2)
            results = cursor.fetchall()

            res_debug2 = '得到返回id'
            logger.info(res_debug2)
            results_debug = '查询所得id : '+str(results[0][0])
            logger.info(results_debug)

            response = {}
            response['status'] = 200
            response['message'] = 'Success'
            response['id'] = results[0][0]
            return json.dumps(response)
        except:
            db.rollback()
        finally:
            db.close()
    else:
        res_debug = '执行失败'
        logger.info(res_debug)
        response = {}
        response['status'] = 500
        response['message'] = 'Fail'
        response['id'] = None
        return json.dumps(response)

@app.route('/queryLostFoundRecord' , methods = ["GET"])
def queryLostFoundRecord():
    phoneNumber = request.args.get('phoneNumber')
    pageSize = request.args.get('pageSize')
    if not isinstance(pageSize , str):  #未读到可选项pageSize
        pageSize = 10                   #设置初值为10
    pageNo = request.args.get('pageNo')
    if not isinstance(pageNo , str):    #未读到可选项pageNo
        pageNo = 1                      #设置初值为1

    phoneNumber_debug = '传入查询参数phoneNumber :' + phoneNumber
    pageSize_debug = '传入查询参数pageSize :' + pageSize
    pageNo_debug = '传入查询参数pageNo :' + pageNo
    logger.info(phoneNumber_debug)
    logger.info(pageSize_debug)
    logger.info(pageNo_debug)

    if not isinstance(phoneNumber , str):  #未读到可选项phoneNumber
        sql = "select * from swuassistant limit %d,%d " % (int(pageSize) * (int(pageNo) - 1) , int(pageSize))

        sql_debug = '传入sql :' + sql
        logger.info(sql_debug)
        pro_debug = '尝试执行queryLostFoundRecord'
        logger.info(pro_debug)

        response = query_function(sql , pageSize , pageNo)
        return json.dumps(response)
    else:                                   #读到可选项phoneNumber
        sql = "select * from swuassistant where phoneNumber = '%s' limit %d , %d " %(str(phoneNumber) , int(pageSize) * (int(pageNo) - 1) , int(pageSize))

        sql_debug = '传入sql :' + sql
        logger.info(sql_debug)
        pro_debug = '尝试执行queryLostFoundRecord'
        logger.info(pro_debug)

        response = query_function(sql , pageSize , pageNo)
        return json.dumps(response)

@app.route('/deleteLostFoundRecord' , methods = ["POST"])
def deleteLostFoundRecord():
    id = request.args.get('id')
    sql = "delete from swuassistant where id = %d" % (int(id))

    id_debug = '传入参数delete_id :' + str(id)
    logger.info(id_debug)
    pro_debug = '尝试执行deleteLostFoundRecord'
    logger.info(pro_debug)

    pro_debug = '尝试寻找是否存在要删除的记录'
    logger.info(pro_debug)
    sql_query = "SELECT DISTINCT IF(EXISTS(SELECT * FROM swuassistant WHERE id = %d),1,0) AS res FROM swuassistant" % (int(id))
    #print(sql_query)

    cursor = db.cursor()
    try:
        db.ping(reconnect=True)
        cursor.execute(sql_query)

        #print(sql_query)
        if cursor:
            res = cursor.fetchall()
            #print(res)
            if res[0][0] == 1:
                res_debug = '结果存在 , 执行删除命令'
                logger.info(res_debug)

                cursor.execute(sql)
                db.commit()
                if cursor:
                    res_debug = '执行成功'
                    logger.info(res_debug)

                    response = {}
                    response['status'] = 200
                    response['message'] = 'Success'
                    response['data'] = None
                    return json.dumps(response)
                else:
                    res_debug = '执行失败'
                    logger.info(res_debug)

                    response = {}
                    response['status'] = 500
                    response['message'] = 'Error'
                    response['data'] = None
                    return json.dumps(response)
            else:
                res_debug = '结果不存在 ，返回'
                logger.info(res_debug)

                response = {}
                response['status'] = 200
                response['message'] = '所需删除记录不存在'
                response['data'] = None
                return json.dumps(response)
        else:
            res_debug2 = '查询失败'
            logger.info(res_debug2)

            response = {}
            response['status'] = 500
            response['message'] = 'Error'
            response['data'] = None
            return json.dumps(response)
    except:
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    app.run()
