#-*- coding: UTF-8 -*-
import json
import MySQLdb
import urllib
import gzip
import tldextract
import time
import datetime
import urllib2


def phishing_gz_download():
    try:
        url = 'http://data.phishtank.com/data/a5ad94d96e7798c38ae9a3092ab45aed1bcbdc8128a6642a6b76f7fa8ebfea56/online-valid.json.gz'
        f = urllib2.urlopen(url)
        data = f.read()
        with open("phishing.gz", "wb") as code:
            code.write(data)
    except Exception,e:
        print e
        phishing_gz_download()


def id_list(db, line):  # 获取phishing_id字段，以判断是插入或是更新
    cursor = db.cursor()
    cursor.execute("select phish_id from phishing_tank")
    data = cursor.fetchall()
    return data


def id_handle(line):  # 字符串处理，来和id_list（）返回值比较
    phish_id = line['phish_id']
    phish_id_handle = phish_id + "L,"
    id_compare = (eval(phish_id_handle))
    return id_compare


def url_extract(url):
    domain_extract = tldextract.extract(url).domain
    suffix = tldextract.extract(url).suffix
    if not suffix:
        insert = domain_extract
        return insert
    else:
        insert = domain_extract + '.' + suffix
        return insert


def mysql_update(cursor, db, line):  # mysql更新操作
    phish_id = line["phish_id"]
    url =line["url"]
    domain = url_extract(url)
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    submission_time = line["submission_time"]
    sql = "update phishing_tank set url =" +"'" + str(url)+ "'" + ",domain = " +"'"+ domain+ "'" + ",submission_time = "+"'" + submission_time +"'" + " WHERE phish_id =" + str(phish_id)
    cursor.execute(sql)
    db.commit()


def mysql_insert(cursor, db, line):  # mysql插入操作
    phish_id = line["phish_id"]
    url = line["url"]
    domain = url_extract(url)
    insert_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    submission_time = line["submission_time"]
    value = [phish_id,url,domain,submission_time,insert_time]
    sql = "insert into phishing_tank values(%s,%s,%s,%s,%s)"
    cursor.execute(sql, value)
    db.commit()


def mysql_handle():  # mysql操作
    try:
        infile = gzip.GzipFile("phishing.gz", "r")
        file = json.load(infile)
    except Exception, e:
        print e
        phishing_gz_download()
        mysql_handle()
    db = MySQLdb.connect(
        "172.29.152.249 ", "root", "platform", "malicious_domain_collection")
    cursor = db.cursor()
    update_count = 0
    insert_count = 0
    for line in file:
        if id_handle(line) in id_list(db, line):
            try:
                mysql_update(cursor, db, line)
                update_count = update_count+ 1
            except:
                continue
        else:
            try:
                mysql_insert(cursor, db, line)
                insert_count = insert_count + 1
            except:
                continue
    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print time
    print "update count:"+update_count
    print "insert count:"+insert_count
    db.close()


def phishing_update_main():  # 主程序入口，同时设定时间：每小时更新一次
    while(1):
        time_start = time.time()
        phishing_gz_download()
        mysql_handle()
        time_end = time.time()
        time_count = time_end - time_start
        if(time_count < 3600):
            time.sleep(3600 - time_count)
            continue
        else:
            continue


if __name__ == "__main__":
    phishing_update_main()

