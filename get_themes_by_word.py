# coding:utf-8
import redis
import json
import time
import requests
import user_agent
import re

r_0 = redis.Redis(host="localhost", port=6379, db=0)

url = "https://www.zhihu.com/api/v4/search_v3?t=column&q={0}&offset={1}&limit=20"

reg = re.compile(r"https://api.zhihu.com/columns/(.+)")

questions = set(user_agent.questions)

for each_question in questions:
    offset = 0
    while True:
        new_list = []
        myurl = url.format(each_question, offset)
        res = requests.get(myurl, headers=user_agent.getheaders())
        js = json.loads(res.content)
        offset += 20
        if js == None:
            break
        data = js.get('data', [])
        for each in data:
            tempurl = each['object']['url']
            theme = str(reg.findall(tempurl)[0])
            article_count = each['object']['articles_count']
            if article_count > 0:
                new_list.append(theme)
        visited_list = r_0.lrange('visited', 0, -1)
        not_visited_list = r_0.lrange('notvisited', 0, -1)
        total_list = set(visited_list) | set(not_visited_list)
        new_themes = set(new_list) - set(total_list)
        for each_theme in new_themes:
            r_0.rpush('notvisited', each_theme)
