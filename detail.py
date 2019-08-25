# coding:utf-8
import requests
import time
import json
import redis
import random
import pymongo
import urllib
import random
import re
import threading 
from threading import Lock
import time
import user_agent

r_0 = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

url_theme = "https://zhuanlan.zhihu.com/api/columns/{0}/articles?limit=20&offset={1}"
url_page = "https://www.zhihu.com/api/v4/articles/{0}?limit=1000&offset=1000"

id = 1 
lock = Lock()

def get_detail(page_url, theme):
    global id
    time.sleep(random.randint(0,2))
    try:
        res_page = None
        res_page = requests.get(page_url, headers=user_agent.getheaders(), timeout=(3,5))
        page_js = json.loads(res_page.content)

        lock.acquire()
        with open('article/{0}.json'.format(id), 'w') as fp:
            print("{}:{}/{}完成".format(theme, id, page_url))
            json.dump(json.loads(json.dumps(page_js)), fp)
            id += 1
        lock.release()
    except Exception as ex:
        print(ex)
    finally:
        if res_page:
            res_page.close()


def get_zhuanlan(theme):
    theme_url = url_theme.format(theme, 1) 
    res = None

    try:
        res = requests.get(theme_url, headers=user_agent.getheaders())
        js = json.loads(res.content)
        total_offset = 100
        if 'paging' in js.keys():
            total_offset = int(js['paging']['totals'])
            print(total_offset)
        else:
            return
        if res:
            res.close()

        offset = 0
        while True:
            if offset > total_offset:
                break
            offset += 20
            try:
               theme_url = url_theme.format(theme, offset-20) 
               res = requests.get(theme_url, headers=user_agent.getheaders())
               temp_js = json.loads(res.content)
               data = temp_js['data']
               ids = [each['id'] for each in data]
               res_page = None

               threads = [threading.Thread(target=get_detail, args=(url_page.format(each_id), theme)) for each_id in ids]
               for thread in threads:
                   thread.setDaemon(True)
                   thread.start()
               for thread in threads:
                   thread.join()
               print("第{}页爬取完成".format(offset))
               #time.sleep(1)
            except Exception as ex:
               print(ex)
            finally:
               if res:
                   res.close()
    except Exception as ex:
        print(ex)
    finally:
        if res:
            res.close()


while True:
    keys = r_0.keys()
    if 'notvisited' not in keys:
        break
    else:
        theme = r_0.rpoplpush('notvisited', 'visited')
        get_zhuanlan(theme)
